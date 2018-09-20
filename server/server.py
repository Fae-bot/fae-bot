import subprocess

from flask import Flask
app = Flask(__name__)

numMotors=4

@app.route('/')
def index():
    return """
    <script>

function post(url) {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", url, true);

	//Send the proper header information along with the request
	xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

	xhr.send("1 0 0 0 1000");
}
</script>



<title>Wirebot debug control</title>
<H1>Wirebot debug control</H1>
<div>MOTOR 1
	<div onClick='post("/motors/1/roll")'>ROLL</div>
	<div onClick='post("/motors/1/unroll")'>UNROLL</div>
</div>
<hr>

<div>MOTOR 2
	<div onClick='post("/motors/2/roll")'>ROLL</div>
	<div onClick='post("/motors/2/unroll")'>UNROLL</div>
</div>
<hr>
<div>MOTOR 3
	<div onClick='post("/motors/3/roll")'>ROLL</div>
	<div onClick='post("/motors/3/unroll")'>UNROLL</div>
</div>
<hr>
<div>MOTOR 4
	<div onClick='post("/motors/4/roll")'>ROLL</div>
	<div onClick='post("/motors/4/unroll")'>UNROLL</div>
</div>

    """
    
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
    app.run(host="0.0.0.0")
