#!/home/pi/bmon/venv/bin/python
from flup.server.fcgi import WSGIServer
import logging
from logging.handlers import RotatingFileHandler
import hw

logfile = "/var/log/lighttpd/hw_daemon.log"
process = hw.process_request()

rot_handler = RotatingFileHandler(logfile, maxBytes=30000, backupCount=5)
logging.basicConfig(
        format="%(asctime)s %(name)s %(module)s:%(lineno)d %(levelname)s:\n    %(message)s",
        handlers = [rot_handler])
logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

logging.getLogger('hw').setLevel(logging.INFO)
logging.getLogger('hw_daemon').setLevel(logging.INFO)
logging.getLogger('dhw_disable').setLevel(logging.INFO)
logger.info(f'Startup.\n')

if __name__ == "__main__":
    WSGIServer(process.doit).run()
