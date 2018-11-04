from time import sleep
import serial
import subprocess

from flask import Flask, render_template_string, render_template, request, send_file, make_response
app = Flask(__name__)

numMotors=4
ind=0
global ser
ser = None
devices = list()
for x in range(10):
	devices.append("/dev/ttyACM" + str(x)) 
	devices.append("/dev/ttyUSB" + str(x))

ind = 0
while ser==None:
	dev = devices[ind%len(devices)]
	try:
		ser = serial.Serial(dev)
		ser.detDTR(False)
		sleep(0.5)
		ser.open()
		
	except:
		print("Could not connect to "+str(dev)+", try again in 1 second")
		ind+=1
		ind = ind % 8
		sleep(1)
		
targets = [0,0,0,0]*16

def motors(m1, m2, m3, m4, dur):
	global ser
	ser.write("s\n")
	ser.write("m 1 "+str(m1)+"\n")
	ser.write("m 2 "+str(m2)+"\n")
	ser.write("m 3 "+str(m3)+"\n")
	ser.write("m 4 "+str(m4)+"\n")
	ser.write("g\n")
	sleep(float(dur))
	ser.write("s\n")


@app.route('/')
def index():
    return  render_template("index.html")

    
@app.route('/motors/<mid>/roll',methods=['POST'])
def rollMotor(mid):
	speed = request.values.get('speed')
	timev = request.values.get('time')
	args = ["0"]*numMotors
	args[int(mid)-1]="-" + speed
	args+=[timev]
	motors(*args)
	return ""

@app.route('/motors/<mid>/unroll',methods=['POST'])
def unrollMotor(mid):
	args = ["0"]*numMotors
	speed = request.values.get('speed')
	timev = request.values.get('time')
	args[int(mid)-1]=speed
	args+=[timev]
	motors(*args)
	return ""

@app.route('/stop',methods=['POST'])
def stopMotors():
	global ser
	ser.write("s\n")
	return ""

@app.route('/set_target/<tid>',methods=['POST'])
def set_target(tid):
	global ser, targets
	ser.write("n "+str(tid)+"\n")
	return ""

@app.route('/go_target/<tid>',methods=['POST'])
def go_target(tid):
	global ser
	speed = request.values.get('speed')
	ser.write("a "+str(tid)+" " + str(speed)+"\n")
	return ""

@app.route('/cycle',methods=['POST'])
def cycle():
	global ser
	speed = request.values.get('speed')
	ser.write("y "+str(speed)+"\n")
	return ""

@app.route('/direction/<direc>',methods=['POST'])
def direction(direc):
	global control_process
	speed = int(request.values.get('speed'))
	timev = float(request.values.get('time'))
	
	if direc == "n":
		motors(speed, speed, -speed, -speed, timev)
	if direc == "s":
		motors(-speed, -speed, speed, speed, timev)
	if direc == "w":
		motors(-speed, speed, -speed, speed, timev)
	if direc == "e":
		motors(speed, -speed, speed, -speed, timev)
	if direc == "nw":
		motors(0, speed, -speed, 0, timev)
	if direc == "ne":
		motors(speed, 0, 0, -speed, timev)
	if direc == "se":
		motors(0, -speed, speed, 0, timev)
	if direc == "sw":
		motors(-speed, 0, 0, speed, timev)
	if direc == "up":
		motors(-speed, -speed, -speed, -speed, timev)
	if direc == "down":
		motors(speed, speed, speed, speed, timev)		
	print timev
	return ""

@app.route('/camera',methods=['GET'])
def camera():
	subprocess.call(["fswebcam", "-r", "640x480", "--no-banner", "--no-overlay", "--no-underlay", "--save", "/tmp/image.jpg"])
        try:
            r = make_response(send_file("/tmp/image.jpg", mimetype='image/jpeg'))
	    r.headers.set('Cache-Control', 'public, max-age=0, no-cache, no-store')
	    return r
        except:
            return""



if __name__ == '__main__':
	try:
		app.run(host="0.0.0.0", port=80, debug = True, threaded=True)
	finally:
		ser.close()
