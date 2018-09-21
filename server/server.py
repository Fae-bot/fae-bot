from time import sleep
import serial

from flask import Flask, render_template_string, render_template, request
app = Flask(__name__)

numMotors=4
ser = serial.Serial("/dev/ttyACM0")

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

@app.route('/direction/<direc>',methods=['POST'])
def direction(direc):
	global control_process
	speed = int(request.values.get('speed'))
	timev = float(request.values.get('time'))
	
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
		
	return ""

if __name__ == '__main__':
	try:
		app.run(host="0.0.0.0", debug = True, threaded=True)
	finally:
		global ser
		ser.close()
