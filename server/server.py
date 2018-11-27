from time import sleep
import serial
import subprocess

from flask import Flask, render_template_string, render_template, request, send_file, make_response
app = Flask(__name__,  static_url_path='/static')

class Fae:
    def __init__(self):
        self.numMotors=4
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
            dev = devices[ind%len(devices)]
            try:
                ser = serial.Serial(dev, baudrate=115200)
                ser.setDTR(False)
                sleep(0.5)
                ser.open()

            except serial.serialutil.SerialException:
                print("Could not connect to "+str(dev)+", try again in 1 second")
                ind+=1
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
        self.serial.write("m 1 "+str(m1)+"\n")
        self.serial.write("m 2 "+str(m2)+"\n")
        self.serial.write("m 3 "+str(m3)+"\n")
        self.serial.write("m 4 "+str(m4)+"\n")
        self.serial.flush()

    def all_speeds(self, s):
        self.motors_speed(s,s,s,s)

    def target(self, t1, t2, t3, t4):
        self.targetPos = [t1, t2, t3, t4]
        self.serial.write("n "+str(t1)+" "+str(t2)+" "+str(t3)+" "+str(t4)+"\n")
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
        self.target(self.lastPos[0] - d1, self.lastPos[1] - d2, self.lastPos[2] - d3, self.lastPos[3] - d4)

    def speed_given_time(self, ttt): # ttt = time to target, in milliseconds
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
            sq += dd**2
        if sq != 0:
            self.motors_speed(speed*d[0]/sq, speed*d[1]/sq, speed*d[2]/sq, speed*d[3]/sq)
        else:
            self.motors_speed(0, 0, 0, 0)


fae = Fae()
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
    fae.speed_given_time(step_size/speed)
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
    fae.speed_given_time(step_size / speed)
    fae.go()
    return ""


@app.route('/stop',methods=['POST'])
def stop_all():
    global fae
    fae.stop()
    return ""


@app.route('/set_target/<tid>',methods=['POST'])
def set_target(tid):
    global targets
    fae.sync()
    targets[int(tid)] = fae.lastPos
    return ""


@app.route('/go_target/<tid>',methods=['POST'])
def go_target(tid):
    global targets, fae
    fae.stop()
    speed = float(request.values.get('speed'))
    fae.target(*targets[int(tid)])
    fae.speed_given_speed(speed)
    fae.go()
    return ""


@app.route('/direction/<direc>',methods=['POST'])
def direction(direc):
    global fae
    fae.stop()
    speed = float(request.values.get('speed'))
    step_size = float(request.values.get('stepsize'))

    if direc == "n":
        fae.delta(step_size, step_size, -step_size, -step_size)
    if direc == "s":
        fae.delta(-step_size, -step_size, step_size, step_size)
    if direc == "w":
        fae.delta(-step_size, step_size, -step_size, step_size)
    if direc == "e":
        fae.delta(step_size, -step_size, step_size, -step_size)
    if direc == "nw":
        fae.delta(0, step_size, -step_size, 0)
    if direc == "ne":
        fae.delta(step_size, 0, 0, -step_size)
    if direc == "se":
        fae.delta(0, -step_size, step_size, 0)
    if direc == "sw":
        fae.delta(-step_size, 0, 0, step_size)
    if direc == "up":
        fae.delta(-step_size, -step_size, -step_size, -step_size)
    if direc == "down":
        fae.delta(step_size, step_size, step_size, step_size)
    fae.speed_given_speed(speed)
    fae.go()
    return ""

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
    app.run(host="0.0.0.0", port=8000, debug=True, threaded=True)

#fae.close()