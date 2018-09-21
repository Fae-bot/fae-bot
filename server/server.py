import subprocess
from time import sleep

from flask import Flask, render_template_string, render_template, request
app = Flask(__name__)

numMotors=4
control_process = None

@app.route('/')
def index():
    return  render_template("index.html")

    
@app.route('/motors/<mid>/roll',methods=['POST'])
def rollMotor(mid):
	global control_process
	speed = request.values.get('speed')
	timev = request.values.get('time')
	args = ["0"]*numMotors
	args[int(mid)-1]="-" + speed
	while control_process != None:
		control_process.wait()
	control_process = subprocess.Popen(["../control",timev]+args)
	control_process.communicate()
	control_process = None
	return ""

@app.route('/motors/<mid>/unroll',methods=['POST'])
def unrollMotor(mid):
	global control_process
	args = ["0"]*numMotors
	speed = request.values.get('speed')
	timev = request.values.get('time')
	args[int(mid)-1]=speed
	while control_process != None:
		control_process.wait()
	control_process = subprocess.Popen(["../control",timev]+args)
	control_process.communicate()
	control_process = None
	return ""

@app.route('/stop',methods=['POST'])
def stopMotors():
	global control_process
	if control_process!=None:
		control_process.kill()
		control_process = None
	return ""

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True, threaded=True)
