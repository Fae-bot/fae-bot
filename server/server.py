from time import sleep
import serial
from math import sqrt
from socket import gethostname
from datetime import datetime as dt

from flask import Flask, render_template_string, render_template, request, send_file, make_response


app = Flask(__name__, static_url_path='/static')


timer = dt.now()


def mtimereset():
    global timer
    timer = dt.now()


def mtime(msg = ""):
    global timer
    n = dt.now()
    print(msg +":"+ " "*(15-len(msg))+str((n-timer).total_seconds()*1000)+" ms")
    timer = n


class Fae:
    def __init__(self):
        self.numMotors = 4
        self.targetPos = [0, 0, 0, 0]
        self.lastPos = [-1, -1, -1, -1]

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
                ser = serial.Serial(dev, baudrate=9600)
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

    def close(self):
        self.serial.close()

    def stop(self):
        self.serial.write("s\n")
        self.serial.flush()

    def go(self):
        self.serial.write("g\n")
        self.serial.flush()

    def motors_speed(self, m1, m2, m3, m4):
        cmd = "m 1 "+str(int(m1))+"\n"
        cmd += "m 2 "+str(int(m2))+"\n"
        cmd += "m 3 "+str(int(m3))+"\n"
        cmd += "m 4 "+str(int(m4))+"\n"
        print(cmd)
        self.serial.write(cmd)
        self.serial.flush()

    def all_speeds(self, s):
        self.motors_speed(s, s, s, s)

    def target(self, t1, t2, t3, t4):
        self.targetPos = [int(t1), int(t2), int(t3), int(t4)]
        cmd = "n "+str(int(t1))+" "+str(int(t2))+" "+str(int(t3))+" "+str(int(t4))+"\n"
        self.serial.write(cmd)
        print(cmd[:-1])
        self.serial.flush()

    def sync(self):
        self.serial.write("p\n")
        self.serial.flush()
        self.lastPos[0] = int(self.serial.readline())
        self.lastPos[1] = int(self.serial.readline())
        self.lastPos[2] = int(self.serial.readline())
        self.lastPos[3] = int(self.serial.readline())

    def delta(self, d1, d2, d3, d4):
        self.sync()
        self.target(self.lastPos[0] + d1, self.lastPos[1] + d2, self.lastPos[2] + d3, self.lastPos[3] + d4)

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



targets = [[0, 0, 0, 0]]*10

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
    fae.delta(*args)
    fae.speed_given_speed(speed)
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
    fae.delta(*args)
    fae.speed_given_speed(speed)
    fae.go()
    return ""


@app.route('/stop', methods=['POST'])
def stop_all():
    global fae
    fae.stop()
    return ""


@app.route('/set_target/<tid>', methods=['POST'])
def set_target(tid):
    global targets
    fae.sync()
    print(targets)
    targets[int(tid)] = list(fae.lastPos)
    print(targets)
    return " ".join([str(x) for x in fae.lastPos])


@app.route('/go_target/<tid>', methods=['POST'])
def go_target(tid):
    global targets, fae
    fae.stop()
    speed = float(request.values.get('speed'))
    print(tid)
    print(targets)
    fae.target(*targets[int(tid)])
    fae.speed_given_speed(speed)
    fae.go()
    print(targets)
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


@app.route('/position', methods=['GET', 'POST'])
def get_position():
    global fae
    fae.sync()
    return " ".join([str(x) for x in fae.lastPos])


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

if gethostname() == "control":
    port = 80
    fae = Fae()
else:
    port = 8000
    #fae = Fae()
    fae = None


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)

#fae.close()
