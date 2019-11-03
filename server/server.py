# Dependencies:
# * Flask
# * pyserial (NOT Serial)
# * ~~pyquaternion~~ -> my modified version fae_quaternion.py
# * numpy

from time import sleep, localtime
import sys
import serial
import threading
from math import sqrt
from socket import gethostname
from datetime import datetime as dt
import json
from threading import Lock
import subprocess as sb
from threading import Thread
import numpy as np
from fae_quaternion import Quaternion
from random import randint, uniform
from http.server import HTTPServer, BaseHTTPRequestHandler, HTTPStatus
import socketserver
import re
from fae.inference import InferenceModel


import numpy as np
import keras
import tensorflow as tf
from keras.models import load_model
from keras.backend import set_session

timer = dt.now()
fae_vision=None
fae_read_thread=None  # Ugly!


def mtimereset():
    global timer
    timer = dt.now()


def mtime(msg=""):
    global timer
    n = dt.now()
    print(msg + ":" + " "*(15-len(msg))+str((n-timer).total_seconds()*1000)+" ms")
    timer = n


global handlers_dict
handlers_dict = dict()


class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def route(path, methods=["GET"]):
    global handlers_dict

    def wrap(func):
        handlers_dict[path] = (func, methods)
        return func
    return wrap


class FaeHttpHandler(BaseHTTPRequestHandler):
    def do_answer(self):
        global handlers_dict
        for p in handlers_dict.keys():
            m = re.match(p + "$", self.path)
            if m:
                print("m", m)
                print("p", p)
                if m.lastindex is None:
                    args = []
                else:
                    args = [m[i] for i in range(1, m.lastindex + 1)]
                print("args ", args)
                values = dict()
                if "Content-Length" in self.headers:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length).decode("ascii")
                    print(post_data)
                    for eq in post_data.split("&"):
                        if "=" in eq:
                            k, v = eq.split("=")
                            values[k]=v

                if "POST" in handlers_dict[p][1]:
                    print(values)
                    answer = handlers_dict[p][0](request_values=values, *args)
                else:
                    answer = handlers_dict[p][0](*args)
                self.send_response(HTTPStatus.OK)
                # self.send_header("Content-type", "text/html;charset=utf-8")
                self.send_header("Content-Length", str(len(answer)))
                self.end_headers()
                if isinstance(answer, str):
                    self.wfile.write(answer.encode("ascii"))
                if isinstance(answer, bytes):
                    self.wfile.write(answer)
                return

    def do_GET(self):
        return self.do_answer()

    def do_POST(self):
        return self.do_answer()


class FaeVision:
    ARTK_PATH = "../../artoolkit5/bin/simpleLite"
    ARTK_ARGS = ['--vconf', '-dev=/dev/video0', '--thresh', '0']
    SUMMATION_PERIOD = 0.2

    def __init__(self):
        self.process = None
        self.poses = list()
        self.thread = Thread(target = self.artk_process)
        self.thread.start()
        self.slock = Lock()
        self.current_time = -1
        self.recording = False

    def artk_process(self):
        self.process = sb.Popen([FaeVision.ARTK_PATH] + FaeVision.ARTK_ARGS,
                                stdout=sb.PIPE,
                                encoding="utf-8",
                                #env={'DISPLAY': ':0'}
                                )
        while self.process.poll() is None:
            line = self.process.stdout.readline()
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
                pos = mat[3,:3]
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
                self.poses.append((current_time, quat, pos))
                self.slock.release()


class MySerial(serial.Serial):
    def write(self, s):
        if type(s) is bytes:
            serial.Serial.write(self, s)
        else:
            serial.Serial.write(self, bytes(s, 'utf-8'))


def read_line_serial(ser):
    global fae_vision
    global fae
    while True:
        try:
            line = ser.readline().decode("utf-8")
            if fae_vision is not None:
                current_time=fae_vision.current_time
                fae.motor_poses.append(str(current_time)+" "+line)

        except serial.serialutil.SerialException:
            pass

class Fae:
    def __init__(self):
        global fae_read_thread
        self.numMotors = 4
        self.targetPos = [0, 0, 0, 0]
        self.lastPos = [-1, -1, -1, -1]
        self.currentSpeed = [0, 0, 0, 0]
        self.slock = Lock()
        self.rlock = Lock()
        self.stopped = False
        self.motor_poses = list()
        self.keras_session = tf.Session()
        self.tf_graph = tf.get_default_graph()
        set_session(self.keras_session)
        self.model = InferenceModel("../notebooks/models/fae.mmp.20191025.bin")


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
                ser = MySerial(dev, baudrate=1000000, timeout=1)
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
        if fae_read_thread==None:
            fae_read_thread = Thread(target=read_line_serial, args=[ser])
            #print("f:"+str(fae_read_thread))
            fae_read_thread.start()

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

    def set_feedback_freq(self, freq):
        cmd = "f "+str(freq)+"\n\r"
        self.slock.acquire()
        self.serial.write(cmd)
        print(cmd[:-1])
        self.serial.flush()
        self.slock.release()

    def sync(self):
        return
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
        self.target(self.lastPos[0] + d1, self.lastPos[1] + d2, self.lastPos[2] + d3, self.lastPos[3] + d4)

    def delta_pos(self, dx, dy, dz):
        global fae_vision
        global tf_graph
        with self.tf_graph.as_default():
            set_session(self.keras_session)
            if fae_vision is not None:
                fae_vision.slock.acquire()
                last_pose = fae_vision.poses[-1]
                fae_vision.slock.release()
                q = last_pose[1]
                newpos = [last_pose[2][0]+dx, last_pose[2][1]+dy, last_pose[2][2]+dz]
                last_pose = list([q.scalar, q.x, q.y, q.z]) + list(last_pose[2])
                ins = np.array([last_pose + newpos])
                print("Ins = "+str(ins))
                target = self.model.inference(ins)

        self.zero()
        self.target(*target)
        self.mode(1)
        self.go()

    def mode(self, mode):
        cmd = "p " + str(mode) + "\n"
        self.slock.acquire()
        self.serial.write(cmd)
        self.serial.flush()
        self.slock.release()
        print(cmd)

    def set_pos(self, pos):
        # Does not work anymore
        self.lastPos = pos
        cmd="z "+" ".join([str(x) for x in pos])+"\n"
        self.slock.acquire()
        self.serial.write(cmd)
        self.serial.flush()
        self.slock.release()
        print(cmd)
        #self.sync()

    def zero(self):
        cmd = "z \n"
        self.slock.acquire()
        self.serial.write(cmd)
        self.serial.flush()
        self.slock.release()
        print(cmd)

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


@route('/')
def index():
    return open("static/index.html").read()


@route('/static/(.*)')
def serve_static_file(path):
    # TODO: paths are not jailed in /static/
    return open("static/"+path, "rb").read()


@route('/motors/([^\/]*)/roll', methods=['POST'])
def roll_motor(mid, request_values):
    global fae
    speed = float(request_values.get('speed'))
    step_size = float(request_values.get('stepsize'))
    fae.stop()
    args = [0]*fae.numMotors
    args[int(mid)-1] = - speed
    fae.motors_speed(*args)
    #fae.speed_given_speed(speed)
    fae.go()
    return ""


@route('/motors/([^\/]*)/unroll', methods=['POST'])
def unroll_motor(mid, request_values):
    global fae
    speed = float(request_values.get('speed'))
    step_size = float(request_values.get('stepsize'))
    fae.stop()
    args = [0] * fae.numMotors
    args[int(mid) - 1] = speed
    fae.motors_speed(*args)
    #fae.speed_given_speed(speed)
    fae.go()
    return ""


@route('/stop', methods=['POST'])
def stop_all(request_values):
    global fae
    fae.stopped = True
    fae.stop()
    fae.mode(0)
    return ""


@route('/set_target/([^\/]*)', methods=['POST'])
def set_target(tid, request_values):
    global fae
    fae.sync()
    fae.targets[str(tid)] = list(fae.lastPos)
    print(fae.targets)
    fae.write_targets()
    return " ".join([str(x) for x in fae.lastPos])


@route('/go_target/([^\/]*)', methods=['POST'])
def go_target(tid, request_values):
    global fae
    fae.stop()
    speed = float(request_values.get('speed'))
    print(tid)
    print(fae.targets)
    fae.target(*fae.targets[str(tid)])
    fae.speed_given_speed(speed)
    fae.go()
    print(fae.targets)
    return ""


@route('/direction/([^\/]*)', methods=['POST'])
def move_direction(direction, request_values):
    global fae
    mtimereset()
    fae.stop()
    mtime("stop")
    speed = float(request_values.get('speed'))
    step_size = float(request_values.get('stepsize'))

    if direction == "n":
        #fae.delta(step_size, step_size, -step_size, -step_size)
        fae.delta_pos(0, 0, -step_size)
    if direction == "s":
        #fae.delta(-step_size, -step_size, step_size, step_size)
        fae.delta_pos(0, 0, step_size)
    if direction == "w":
        #fae.delta(-step_size, step_size, -step_size, step_size)
        fae.delta_pos(-step_size, 0, 0)
    if direction == "e":
        #fae.delta(step_size, -step_size, step_size, -step_size)
        fae.delta_pos(step_size, 0, 0)
    if direction == "nw":
        #fae.delta(0, step_size, -step_size, 0)
        fae.delta_pos(-step_size, 0, -step_size)
    if direction == "ne":
        #fae.delta(step_size, 0, 0, -step_size)
        fae.delta_pos(step_size, 0, -step_size)
    if direction == "se":
        #fae.delta(0, -step_size, step_size, 0)
        fae.delta_pos(step_size, 0, step_size)
    if direction == "sw":
        #fae.delta(-step_size, 0, 0, step_size)
        fae.delta_pos(-step_size, 0, step_size)
    if direction == "up":
        #fae.delta(-step_size, -step_size, -step_size, -step_size)
        fae.delta_pos(0, step_size, 0)
    if direction == "down":
        #fae.delta(step_size, step_size, step_size, step_size)
        fae.delta_pos(0, -step_size, 0)
    mtime("delta")
    fae.speed_given_speed(speed)
    mtime("speed")
    fae.go()
    mtime("go")
    return ""


@route('/randomize', methods=['POST'])
def randomize(request_values):
    segDur = float(request_values.get('segDur'))
    numSegs = float(request_values.get('numSegs'))
    numCyc = float(request_values.get('numCyc'))


    # Make <numCyc> cycles of <numSegs> random moves of <segDur> sec
    fae.stopped = False
    max_speed = float(request_values.get('speed'))
    fae.zero()

    for c in range(numCyc):
        # Go back to zero
        fae.target(0, 0, 0, 0)
        fae.mode(1)
        fae.go()
        finished = False
        # Wait for the movement toward 0 to finish
        while not finished:
            sleep(1)
            try:
                fae.slock.acquire()
                fae.serial.write("p\r\n")
                fae.serial.flush()
                line = fae.serial.readline().decode("utf-8")
                pos = [int(x) for x in line.rstrip("\n\r ").split(" ")]
                print("SYNC "+str(pos))
            finally:
                fae.slock.release()
            if pos[0] == 0 and pos[1] == 0 and pos[2] == 0 and pos[3] == 0:
                finished = True
        
        for k in range(numSegs):
            motors_speed = list()
            for im in range(4):
                v = uniform(max_speed, 3 * max_speed)
                v *= randint(0, 1)*2 - 1
                motors_speed.append(v)
            fae.motors_speed(*motors_speed)
            fae.go()
            sleep(segDur)
            if fae.stopped:
                break
            fae.stop()
    return ""


@route('/record', methods=['POST'])
def record(request_values):
    global fae_vision
    print("Starting fae vision")
    fae_vision = FaeVision()
    print("ha")
    t = localtime()
    filename = f"coords-{t.tm_year}-{t.tm_mon}-{t.tm_mday}-{t.tm_hour}-{t.tm_min}-{t.tm_sec}.txt"
    # Trust Flask to handle this in a separate thread
    f = open(filename, "w")
    fae_vision.recording = True
    while fae_vision.recording:
        fae_vision.slock.acquire()
        current_time = fae_vision.current_time
        poses = fae_vision.poses
        fae_vision.poses = list()
        fae_vision.slock.release()
        fae.rlock.acquire()
        speeds = fae.currentSpeed
        mposes = fae.motor_poses
        fae.motor_poses = list()

        fae.rlock.release()
        for p in poses:
            s = "p " + str(p[0])
            q = p[1]
            pos = p[2]
            s += f" {q.scalar} {q.x} {q.y} {q.z} {pos[0]} {pos[1]} {pos[2]}\n"
            #print(s)
            f.write(s)
        #f.write("m " + str(current_time) + " " + " ".join([str(s) for s in speeds]) + "\n")
        for mp in mposes:
            s = "f " + str(mp)+"\n"
            #print(s)
            f.write(s)
        if not fae.stopped:
            f.write("m " + str(current_time) + " " + " ".join([str(s) for s in speeds]) + "\n")
        f.flush()
        sleep(0.1)
    f.close()
    return ""

@route('/stop_record', methods=['POST'])
def stop_record(request_values):
    global fae_vision
    fae_vision.recording = False
    fae_vision.process.kill()
    return ""


@route('/position', methods=['GET', 'POST'])
def get_position(request_values={}):
    return "0 0 0 0"
    #global fae
    #fae.sync()
    #return " ".join([str(x) for x in fae.lastPos])


@route('/targets', methods=['GET'])
def get_targets():
    global fae
    return json.dumps(fae.targets)

"""@route('/camera',methods=['GET'])
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
        fae.set_feedback_freq(50)

    else:
        port = 8000
        # fae = Fae()
        fae = None

    #app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
    httpd = ThreadingHTTPServer(("", port), FaeHttpHandler)
    httpd.serve_forever()
