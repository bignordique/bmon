#!/home/pi/bmon/venv/bin/python
import time
import logging
from hw_pump_pexpect import pump_pexpect

class hw_daemon(pump_pexpect):

    def __init__ (self):
        pump_pexpect.__init__(self)
        self.logger = logging.getLogger(__name__ + f'_inst')

    def set_get_pump(self, minutes):
        return ({"pump_on": 1, "pump_off":2})

    def set_get_vacay(self, days):
        return ({"days_remaining": 1})

    def loop(self):
        while True:
            time.sleep(1)
        
