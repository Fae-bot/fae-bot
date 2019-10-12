# Dependencies:
# * Flask
# * pyserial (NOT Serial)
# * ~~pyquaternion~~ -> my modified version fae_quaternion.py
# * numpy

from time import sleep, localtime
import sys
import serial
from math import sqrt
from socket import gethostname
from datetime import datetime as dt
import json
from flask import Flask, render_template_string, render_template, request, send_file, make_response
from threading import Lock
import subprocess as sb
from threading import Thread
import numpy as np
from fae_quaternion import Quaternion
from random import randint, uniform

app = Flask(__name__, static_url_path='/static')


timer = dt.now()


def mtimereset():
    global timer
    timer = dt.now()


def mtime(msg=""):
    global timer
    n = dt.now()
    print(msg + ":" + " "*(15-len(msg))+str((n-timer).total_seconds()*1000)+" ms")
    timer = n


class FaeVision:
    ARTK_PATH = "../../artoolkit5/bin/simpleLite"
    ARTK_ARGS = ['--vconf', '-dev=/dev/video0', '--thresh', '3']
    SUMMATION_PERIOD = 0.2

    def __init__(self):
        self.process = None
        self.orientations = list()
        self.thread = Thread(target = self.artk_process)
        self.thread.start()
        self.slock = Lock()
        self.current_time = -1
        self.recording = False

    def artk_process(self):
        self.process = sb.Popen([FaeVision.ARTK_PATH] + FaeVision.ARTK_ARGS,
                                stdout=sb.PIPE,
                                encoding="utf-8",
                                env={'DISPLAY': ':0'})
        while self.process.poll() is None:
            line = self.process.stdout.readline()
            print(line)
            arr = line.rstrip().split(" ")
            sum_v = Quaternion(scalar=0, vector=(0, 0, 0))
            sum_count = 0
            sum_last_time = -1
            if len(arr) == 17:
                current_time = float(arr[0])
                if sum_last_time < 0:
                    sum_last_time = current_time
                mat = np.array([float(a) for a in arr[1:]])
                mat = mat.reshape(4, 4)
                mat = mat[:3, :3]
                quat = Quaternion(matrix=mat[:3, :3], force_imperfect=True)
                """if current_time-sum_last_time < FaeVision.SUMMATION_PERIOD:
                    sum_v += quat
                    sum_count += 1
                else:
                    if sum_count > 0:
                        self.current_time = current_time
                        self.orientations.append((current_time, sum_v/sum_count))
                """
                self.slock.acquire()
                self.current_time = current_time
                self.orientations.append((current_time, quat))
                self.slock.release()


class MySerial(serial.Serial):
    def write(self, s):
        if type(s) is bytes:
            serial.Serial.write(self, s)
        else:
            serial.Serial.write(self, bytes(s, 'utf-8'))


class Fae:
    def __init__(self):
        self.numMotors = 4
        self.targetPos = [0, 0, 0, 0]
        self.lastPos = [-1, -1, -1, -1]
        self.currentSpeed = [0, 0, 0, 0]
        self.slock = Lock()
        self.rlock = Lock()

        # Connect to the USB serial
        devices = list()
        for x in range(10):
            devices.append("/dev/ttyACM" + str(x))
            devices.append("/dev/ttyUSB" + str(x))

        ser = None
        ind = 0
        while ser is None:
            dev = devices[ind % len(devices)]
            try:
                #ser = serial.Serial(dev, baudrate=9600)
                ser = MySerial(dev, baudrate=1000000)
                ser.setDTR(False)
                sleep(0.5)
                #ser.open()
                print(" * Fae controller found as device"+dev)
            except serial.serialutil.SerialException as e:
                #print(str(e))
                print("Could not connect to "+str(dev)+", try again in 1 second")
                ind += 1
                ind = ind % 8
                sleep(1)
        self.serial = ser

        self.targets = dict()
        # Reload targets if available
        try:
            fb = open("targets", "r")
            for line in fb.read().split("\n"):
                arr = line.split(" ")
                if len(arr) < 5:
                    continue
                self.targets[" ".join(arr[:-4])] = [int(arr[-4]), int(arr[-3]), int(arr[-2]), int(arr[-1])]
            fb.close()
        except Exception as e:
            print(e)
            pass
        print(" * Targets: " + str(self.targets))
        # Reload last position
        try:
            f = open("last_pos")
            pos = [int(x) for x in f.read().split(" ")]
            print(pos, len(pos))
            if len(pos)==4:
                self.lastPos = pos
                self.set_pos(self.lastPos)
        except Exception as e:
            print(e)
            try:
                self.slock.release()
            except RuntimeError:
                pass
            pass
        print(" * Last position: " + str(self.lastPos))

    def close(self):
        self.sync()
        self.serial.close()

    def write_position(self):
        try:
            f = open("last_pos", "w")
            content = " ".join([str(x) for x in self.lastPos])+"\n"
            f.write(content)
            print("Wrote:"+repr(content))
        except Exception as e:
            print(" * Could not write position: "+str(e))

    def stop(self):
        #self.slock.acquire()
        self.serial.flush()
        self.serial.write("s\n")
        self.serial.flush()
        #self.slock.release()

    def go(self):
        self.slock.acquire()
        print("lock acquired")
        self.serial.write("g\n")
        print("g")
        self.serial.flush()
        self.slock.release()
        print("lock release")

    def motors_speed(self, m1, m2, m3, m4):
        self.rlock.acquire()
        self.currentSpeed = [m1,m2,m3,m4]
        self.rlock.release()
        cmd = "m 1 "+str(int(m1))+"\n"
        cmd += "m 2 "+str(int(m2))+"\n"
        cmd += "m 3 "+str(int(m3))+"\n"
        cmd += "m 4 "+str(int(m4))+"\n"
        print(cmd)
        self.slock.acquire()
        print("lock acquired")
        self.serial.write(cmd)
        self.slock.release()
        print("lock released")
        self.serial.flush()

    def all_speeds(self, s):
        self.motors_speed(s, s, s, s)

    def target(self, t1, t2, t3, t4):
        self.targetPos = [int(t1), int(t2), int(t3), int(t4)]
        cmd = "n "+str(int(t1))+" "+str(int(t2))+" "+str(int(t3))+" "+str(int(t4))+"\n"
        self.slock.acquire()
        self.serial.write(cmd)
        print(cmd[:-1])
        self.serial.flush()
        self.slock.release()

    def sync(self):
        try:
            self.slock.acquire()
            self.serial.write("p\r\n")
            self.serial.flush()
            line = self.serial.readline().decode("utf-8")
            self.lastPos = [int(x) for x in line.rstrip("\n\r ").split(" ")]
            self.write_position()
            print(repr(line))
            print("SYNC "+str(self.lastPos))
        finally:
            self.slock.release()

    def delta(self, d1, d2, d3, d4):
        self.sync()
        self.target(self.lastPos[0] + d1, self.lastPos[1] + d2, self.lastPos[2] + d3, self.lastPos[3] + d4)

    def set_pos(self, pos):
        self.lastPos = pos
        cmd="z "+" ".join([str(x) for x in pos])+"\n"
        self.slock.acquire()
        self.serial.write(cmd)
        self.serial.flush()
        self.slock.release()
        print(cmd)
        #self.sync()

    def speed_given_time(self, ttt):  # ttt = time to target, in milliseconds
        self.sync()
        d = [self.targetPos[i] - self.lastPos[i] for i in range(self.numMotors)]
        speeds = [0] * self.numMotors
        for i in range(fae.numMotors):
            if d[i] != 0:
                speeds[i] = ttt/d[i]
        self.motors_speed(*speeds)

    def speed_given_speed(self, speed):
        self.sync()
        d = [self.targetPos[i] - self.lastPos[i] for i in range(self.numMotors)]
        sq = 0
        for dd in d:
            sq += float(dd**2)
        sq = sqrt(sq)
        if sq != 0:
            self.motors_speed(float(speed)*d[0]/sq,
                              float(speed)*d[1]/sq,
                              float(speed)*d[2]/sq,
                              float(speed)*d[3]/sq)
        else:
            self.motors_speed(0, 0, 0, 0)

    def write_targets(self):
        fb = open("targets", "w")
        for k, v in self.targets.items():
            fb.write(k + " " + " ".join([str(c) for c in v]) + "\n")


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/motors/<mid>/roll', methods=['POST'])
def roll_motor(mid):
    global fae
    speed = float(request.values.get('speed'))
    step_size = float(request.values.get('stepsize'))
    fae.stop()
    args = [0]*fae.numMotors
    args[int(mid)-1] = - step_size
    fae.motors_speed(*args)
    #fae.speed_given_speed(speed)
    fae.go()
    return ""


@app.route('/motors/<mid>/unroll', methods=['POST'])
def unroll_motor(mid):
    global fae
    speed = float(request.values.get('speed'))
    step_size = float(request.values.get('stepsize'))
    fae.stop()
    args = [0] * fae.numMotors
    args[int(mid) - 1] = step_size
    fae.motors_speed(*args)
    #fae.speed_given_speed(speed)
    fae.go()
    return ""


@app.route('/stop', methods=['POST'])
def stop_all():
    global fae
    fae.stop()
    return ""


@app.route('/set_target/<tid>', methods=['POST'])
def set_target(tid):
    global fae
    fae.sync()
    fae.targets[str(tid)] = list(fae.lastPos)
    print(fae.targets)
    fae.write_targets()
    return " ".join([str(x) for x in fae.lastPos])


@app.route('/go_target/<tid>', methods=['POST'])
def go_target(tid):
    global fae
    fae.stop()
    speed = float(request.values.get('speed'))
    print(tid)
    print(fae.targets)
    fae.target(*fae.targets[str(tid)])
    fae.speed_given_speed(speed)
    fae.go()
    print(fae.targets)
    return ""


@app.route('/direction/<direction>', methods=['POST'])
def move_direction(direction):
    global fae
    mtimereset()
    fae.stop()
    mtime("stop")
    speed = float(request.values.get('speed'))
    step_size = float(request.values.get('stepsize'))

    if direction == "n":
        fae.delta(step_size, step_size, -step_size, -step_size)
    if direction == "s":
        fae.delta(-step_size, -step_size, step_size, step_size)
    if direction == "w":
        fae.delta(-step_size, step_size, -step_size, step_size)
    if direction == "e":
        fae.delta(step_size, -step_size, step_size, -step_size)
    if direction == "nw":
        fae.delta(0, step_size, -step_size, 0)
    if direction == "ne":
        fae.delta(step_size, 0, 0, -step_size)
    if direction == "se":
        fae.delta(0, -step_size, step_size, 0)
    if direction == "sw":
        fae.delta(-step_size, 0, 0, step_size)
    if direction == "up":
        fae.delta(-step_size, -step_size, -step_size, -step_size)
    if direction == "down":
        fae.delta(step_size, step_size, step_size, step_size)
    mtime("delta")
    fae.speed_given_speed(speed)
    mtime("speed")
    fae.go()
    mtime("go")
    return ""


@app.route('/randomize', methods=['POST'])
def randomize():
    # Make 6 random moves of 1 sec
    for k in range(6):
        motors_speed = list()
        for im in range(4):
            v = uniform(40, 100)
            v *= randint(0, 1)*2 - 1
            motors_speed.append(v)
        fae.motors_speed(*motors_speed)
        fae.go()
        sleep(1)
        fae.stop()
    return ""


@app.route('/record', methods=['POST'])
def record():
    global fae_vision
    print("Starting fae vision")
    fae_vision = FaeVision()

    t = localtime()
    filename = f"coords-{t.tm_year}-{t.tm_mon}-{t.tm_mday}-{t.tm_hour}-{t.tm_min}-{t.tm_sec}.txt"
    # Trust Flask to handle this in a separate thread
    f = open(filename, "w")
    fae_vision.recording = True
    while fae_vision.recording:
        fae_vision.slock.acquire()
        current_time = fae_vision.current_time
        poses = fae_vision.orientations
        fae_vision.orientations = list()
        fae_vision.slock.release()
        fae.rlock.acquire()
        speeds = fae.currentSpeed
        fae.rlock.release()
        for p in poses:
            s = "p " + str(p[0])
            print(p)
            q = p[1]
            s += f" {q.scalar} {q.x} {q.y} {q.z}\n"
            f.write(s)
        f.write("m " + str(current_time) + " " + " ".join([str(s) for s in speeds]) + "\n")
        f.flush()
        sleep(0.1)
    f.close()
    return ""

@app.route('/stop_record', methods=['POST'])
def stop_record():
    global fae_vision
    fae_vision.recording = False
    fae_vision.process.kill()
    fae_vision = None
    return ""


@app.route('/position', methods=['GET', 'POST'])
def get_position():
    return "0 0 0 0"
    #global fae
    #fae.sync()
    #return " ".join([str(x) for x in fae.lastPos])


@app.route('/targets', methods=['GET'])
def get_targets():
    global fae
    return json.dumps(fae.targets)

"""@app.route('/camera',methods=['GET'])
def camera():
    subprocess.call(["fswebcam", "-r", "640x480", "--no-banner", "--no-overlay", "--no-underlay", "--save", "/tmp/image.jpg"])
        try:
            r = make_response(send_file("/tmp/image.jpg", mimetype='image/jpeg'))
        r.headers.set('Cache-Control', 'public, max-age=0, no-cache, no-store')
        return r
        except:
            return""


"""
if __name__ == '__main__':
    if gethostname() == "control" or "control" in sys.argv:
        port = 80
        fae = Fae()

    else:
        port = 8000
        # fae = Fae()
        fae = None

    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
