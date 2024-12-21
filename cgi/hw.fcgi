#!/home/pi/bmon/venv/bin/python
from flup.server.fcgi import WSGIServer
import hw

process = hw.process_request()

if __name__ == "__main__":
    WSGIServer(process.doit).run()
