from gevent.wsgi import WSGIServer
from server import app

http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()