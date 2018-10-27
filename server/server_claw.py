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
		ser = serial.Serial("/dev/ttyUSB"+str(ind), baudrate=57600)
		ser.detDTR(False)
		sleep(0.5)
		ser.open()
		
	except:
		print("Could not connect to /dev/ttyUSB"+str(ind)+", try again in 1 second")
		ind+=1
		ind = ind % 8
		sleep(1)
		
targets = [0,0,0,0]*16
@app.route('/')
def index():
    return  render_template("index_claw.html")

    
@app.route('/claw/<val>',methods=['POST'])
def claw(val):
	global ser
	try:
		ser.flushOutput()
		ser.write(str(val)+"\n")
		ser.flushOutput()
		print("Sent "+str(val))
		
	except:
		print("Writing to serial port failed. Trying again")
		ser=None
		ind=0
		while ser==None:		
			try:
				ser = serial.Serial("/dev/ttyUSB"+str(ind), baudrate=57600)
				ser.detDTR(False)
				sleep(0.5)
				ser.open()
				sleep(0.5)
				ser.write(str(val)+"\n")
				ser.flush()
				print("Sent "+str(val))
			except:
				print("Could not connect to /dev/ttyUSB"+str(ind)+", try again in 1 second")
				ind+=1
				ind = ind % 8
				sleep(1)
	
	return ""

if __name__ == '__main__':
	try:
		app.run(host="0.0.0.0", port = 5001, debug = True, threaded=True)
	finally:
		ser.close()
