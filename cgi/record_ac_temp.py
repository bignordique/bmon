#!/home/leith/bmon/.venv/bin/python

import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import json

EXE_LOGFILE = "/var/log/lighttpd/cellar_temp_exe.log"
RIGID_AC_TEMP_FILE = "/tmp/rigid_ac_temp"

if __name__ == "__main__":

# Just use root handler.   Configure to only output to EXE_LOGFILE
    logging.basicConfig(level=logging.INFO, 
                        handlers=[RotatingFileHandler(EXE_LOGFILE, 'a', maxBytes=10000, backupCount=2)],
                        format="%(asctime)s %(name)s %(module)s:%(lineno)d %(levelname)s:\n    %(message)s\n")
#    print (f'logging.handlers: {logging.handlers}', file=sys.stderr)

    environ = ""
    for param in sorted(os.environ.keys()):
        environ += f'{param}:{os.environ[param]}'
    bytes_received = int(os.environ["CONTENT_LENGTH"])
    post_bytes = sys.stdin.read(bytes_received)
    logging.debug (f'bytes_received: {bytes_received}  bytes: {post_bytes}')

    try:
        with open(RIGID_AC_TEMP_FILE, "w") as f:
            f.write(post_bytes)
    except Exception as e:
        logging.error(f'File write error: {e}')


    print("abide", end="")

