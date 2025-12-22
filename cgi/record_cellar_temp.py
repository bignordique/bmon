#!/home/leith/bmon/.venv/bin/python

import logging
from logging.handlers import RotatingFileHandler

EXE_LOGFILE = "/var/log/lighttpd/cellar_temp_exe.log"
CELLAR_TEMP_FILE = "/tmp/cellar_temp"

class record_cellar_temp():
    def __init__(self):
        
        logging.basicConfig(filename=EXE_LOGFILE,
            format="%(asctime)s %(name)s %(module)s:%(lineno)d %(levelname)s:\n    %(message)s\n")
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler = RotatingFileHandler(filename=EXE_LOGFILE, maxBytes=10000, backupCount=2)
        self.logger.info(f'hello world\n')


if __name__ == "__main__":

    rct = record_cellar_temp()



