#!/home/pi/bmon/venv/bin/python
import time
import logging
import threading
from hw_pump_pexpect import pump_pexpect
from cron_entry import cron_entry
from dhw_disable import dhw_disable

class hw_daemon(pump_pexpect):

    def __init__ (self):
        pump_pexpect.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.dhw_disable_inst = dhw_disable()
        self.pump_is_on = False
        self.set_15 = True
        self.pump_run_interval = 15 * 60
        self.pump_off = 0
        self.pump_on = 0
        self.vacay_days = 0
        self.hw_pump_week = cron_entry("hw_pump_week", "5,35 5-7,16-21 * * mon-fri", self.set_pump_on)
        self.hw_pump_wkend = cron_entry("hw_pump_wkend", "5,35 5-21 * * sat-sun", self.set_pump_on)
        self.once_a_day = cron_entry("once_a_day", "0 0 * * *", self.adjust_vacay)
        thread = threading.Thread(target = self.loop, daemon= True)
        thread.start()

    def set_get_pump(self, minutes):
        if minutes == 15 : self.set_pump_on()

        remaining = self.pump_off - int(time.time())
        if self.pump_is_on:
            diff = int(time.time()) - self.pump_on
        else:
            diff = int(time.time()) - self.pump_off

        m, s = divmod(diff,60)
        h, m = divmod(m,60)

        rm, rs = divmod(remaining,60)
        rh, rm = divmod(rm,60)

        if self.pump_is_on:
            out_string = f'Pump running: {h:d}:{m:02d}:{s:02d} - {rh:d}:{rm:02d}:{rs:02d} remaining'
        else:
            out_string = f'Pump off: {h:d}:{m:02d}:{s:02d}'

        return ({"value": out_string})

    def set_get_vacay(self, days):
        int_days = int(days)
        if self.vacay_days == 15 and int_days == 1 or self.vacay_days == 0 and int_days == -1:
           return ({"value": self.vacay_days, "vacay_warning": "True"})
        self.vacay_days = self.vacay_days + int_days
        return ({"value": self.vacay_days, "vacay_warning": "False"})

    def set_get_alexa(self, minutes):
        if minutes == 15 : self.set_pump_on = True
        return ({"pump_off": self.pump_off, "pump_on":self.pump_on, "vacay_days": self.vacay_days})

    def set_pump_on(self):
        self.set_15 = True

    def adjust_vacay(self):
        self.vacay_days = max(0, self.vacay_days - 1)

    def loop(self):
        while True:
            time.sleep(1)   # wait at startup... might avoid conflicts
            self.hw_pump_week.check_entry()
            self.hw_pump_wkend.check_entry()
            self.once_a_day.check_entry()
        
            epoch_time = int(time.time())

            if ((self.pump_off < epoch_time and not self.set_15) or self.vacay_days > 0) and self.pump_is_on:
                self.pump_off = epoch_time
                self.pump_command("off")
                self.logger.debug(f'pump off\n')
                self.pump_is_on = False

            if self.vacay_days > 0: self.set_15 = False

            if self.set_15:
                self.pump_off = epoch_time + self.pump_run_interval
                self.pump_command("on")
                self.logger.debug(f'pump on\n')
                if not self.pump_is_on : self.pump_on = epoch_time
                self.pump_is_on = True
                self.set_15 = False

            self.dhw_disable_inst.check_dhw(self.pump_is_on)

if __name__ == "__main__":


    logging.basicConfig(format='%(asctime)s %(name)s %(module)s:%(lineno)d %(levelname)s:\n%(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    logger.debug(f'    Starting thread.')

    a = hw_daemon()

    a.set_get_pump("15")

    time.sleep(10)
