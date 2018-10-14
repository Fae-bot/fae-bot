from time import sleep
import serial

from flask import Flask, render_template_string, render_template, request
app = Flask(__name__)

numMotors=4
global ser
ser=None
ind=0
while ser==None:
	try:
		ser = serial.Serial("/dev/ttyUSB"+str(ind))
		
	except:
		print("Could not connect to /dev/ttyUSB"+str(ind)+", try again in 1 second")
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
    return  render_template("index_claw.html")

    
@app.route('/claw/<val>',methods=['POST'])
def claw(val):
	global ser
	ser.write(str(val)+"\n")
	return ""

if __name__ == '__main__':
	try:
		app.run(host="0.0.0.0", port = 5001, debug = True, threaded=True)
	finally:
		global ser
		ser.close()
