import subprocess

from flask import Flask, render_template_string, render_template
app = Flask(__name__)

numMotors=4

@app.route('/')
def index():
    return  render_template("index.html")

    
@app.route('/motors/<mid>/roll',methods=['POST'])
def rollMotor(mid):
	args = ["0"]*numMotors
	args[int(mid)-1]="-1000"
	subprocess.check_call(["../control","1"]+args)
	return ""

@app.route('/motors/<mid>/unroll',methods=['POST'])
def unrollMotor(mid):
	args = ["0"]*numMotors
	args[int(mid)-1]="1000"
	subprocess.check_call(["../control","1"]+args)
	return ""

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True)
