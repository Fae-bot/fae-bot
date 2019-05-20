from pprint import pprint
import subprocess as sb
from threading import Thread

ARTK_PATH = "../../artoolkit5/bin/simpleLite"
ARTK_ARGS = ['--vconf', '-dev=/dev/video0', '--thresh', '2']

lines = list()
process = None


def artk_process():
    global lines, process
    process = sb.Popen([ARTK_PATH] + ARTK_ARGS,
                       stdout=sb.PIPE,
                       stderr=sb.PIPE,
                       encoding="utf-8",
                       env={'DISPLAY': ':0'})
    while process.poll() is None:
        #l = process.stdout.readline()
        l = process.stdout.readline()
        lines.append(l)
        #print(l)
        #print("added")
        pass


thr = Thread(target=artk_process)
thr.start()

lastlen = 0
try:
    while len(lines)<1000:
        if lastlen != len(lines):
            pprint(lines[lastlen:len(lines)])
            lastlen = len(lines)
            #print(len(lines))

except KeyboardInterrupt:
    pass
process.kill()
