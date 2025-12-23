#!/home/leith/bmon/.venv/bin/python

import logging
from logging.handlers import RotatingFileHandler
import cgitb
import os

EXE_LOGFILE = "/var/log/lighttpd/cellar_temp_exe.log"
CELLAR_TEMP_FILE = "/tmp/cellar_temp"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
            format="%(asctime)s %(name)s %(module)s:%(lineno)d %(levelname)s:\n    %(message)s\n")
    logger = logging.getLogger(__name__)
# Does not delete stdout handler.   OK since stdout inside lighttpd goes to /dev/null (I think)
    logger.addHandler(RotatingFileHandler(EXE_LOGFILE, maxBytes=10000, backupCount=2))
    logger.info(f'hello world\n')


    for param in sorted(os.environ.keys()):
        print (f'{param}:{os.environ[param]}')


