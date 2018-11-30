from time import sleep
import serial
import subprocess
from socket import gethostname

from flask import Flask, render_template_string, render_template, request, make_response, send_file
app = Flask(__name__)


class FaeClaw:
    def __init__(self, skip=False):
        # Connect to the USB serial
        devices = list()
        for x in range(10):
            devices.append("/dev/ttyACM" + str(x))
            devices.append("/dev/ttyUSB" + str(x))

        ser = None
        ind = 0
        if not skip:
            while ser is None:
                dev = devices[ind % len(devices)]
                try:
                    ser = serial.Serial(dev, baudrate=57600)
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
        self.bookmarks = dict()
        # Reload bookmark if available
        try:
            fb = open("bookmarks", "r")
            for line in fb.read().split("\n"):
                arr = line.split(" ")
                if len(arr)<2:
                    continue
                self.bookmarks[" ".join(arr[:-1])] = int(arr[-1])
            fb.close()
        except Exception as e:
            print(e)
            pass
        print(" * Bookmarks: " + str(self.bookmarks))

    def close(self):
        if self.serial is not None:
            self.serial.close()

    def set_pos(self, pos):
        if self.serial is not None:
            self.serial.flushOutput()
            self.serial.write(str(pos) + "\n")
            self.serial.flushOutput()
        print("Sent " + str(pos))

    def set_bookmark(self, name, pos):
        self.bookmarks[name] = pos
        fb = open("bookmarks", "w")
        for k,v in self.bookmarks.items():
            fb.write(k+ " " + str(v)+"\n")
        fb.close()

    def go_name(self, name):
        if self.bookmarks.has_key(name):
            self.set_pos(self.bookmarks[name])


global claw
if gethostname() == "claw":
    claw = FaeClaw()
else:
    claw = FaeClaw(skip=True)


@app.route('/')
def index():
    return render_template("index_claw.html")

    
@app.route('/claw/<val>', methods=['POST'])
def set_value(val):
    global claw
    claw.set_pos(val)
    return ""


@app.route('/claw/set_open/<val>', methods=['POST'])
def set_open(val):
    global claw
    claw.set_bookmark("open", val)
    return ""


@app.route('/claw/set_closed/<val>', methods=['POST'])
def set_closed(val):
    global claw
    claw.set_bookmark("closed", val)
    return ""


@app.route('/claw/go_open', methods=['POST'])
def go_open():
    global claw
    claw.go_name("open")
    return ""


@app.route('/claw/go_closed', methods=['POST'])
def go_closed():
    global claw
    claw.go_name("closed")
    return ""


@app.route('/camera', methods=['GET'])
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
        app.run(host="0.0.0.0", port = 5001, debug = True, threaded=True)
    finally:
        claw.close()
