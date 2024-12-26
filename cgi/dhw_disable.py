#!/home/pi/bmon/venv/bin/python

# Only enable dhw_disable on the positive edge of is_night.   If dhw_disable is
# disabled in the middle of is_night, it won't enable until the next
# positive edge of is_night.

import RPi.GPIO as GPIO
from in_window import in_window
import logging

class dhw_disable ():

    def __init__ (self, bit=18, start = "0-59/30 0 * * *", end = "15-59/30 4 * * *"):
        self.logger = logging.getLogger("dhw_disable")
        self.bit = bit
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(bit, GPIO.OUT)
        self.set_dhw_disable()
        self.night_window = in_window("night_window", start , end)
        self.was_night = self.night_window.check()

    def set_dhw_disable(self):
        if GPIO.input(self.bit) == GPIO.HIGH:
            GPIO.output(self.bit, GPIO.LOW)
            self.report_dhw()

    def set_dhw_enable(self):
        if GPIO.input(self.bit) == GPIO.LOW:
            GPIO.output(self.bit, GPIO.HIGH)
            self.report_dhw()

    def report_dhw(self):
        self.logger.debug(f'dhw bit equals: {GPIO.input(self.bit)}')

    def check_dhw(self, pump_running):

        is_night = self.night_window.check()

        if is_night and not self.was_night and not pump_running :
            self.set_dhw_enable()

        if not is_night or pump_running : 
            self.set_dhw_disable()

        """
        self.logger.debug(f'pump_running: {pump_running}' + \
                          f'  is_night: {is_night}' + \
                          f'  was_night: {self.was_night}' + \
                          f'  dhw bit equals: {GPIO.input(self.bit)}')
        """

        self.was_night = is_night

if __name__ == "__main__":

    import time

    dhw_disable_bit = 18

    logging.basicConfig(format="%(asctime)s %(name)s %(module)s:%(lineno)d " + 
                        "%(levelname)s:\n    %(message)s\n")


    start = "0-59/30 * * * *"
    end = "15-59/30 * * * *"
    start = "0-58/2  * * * *" 
    end = "1-59/2  * * * *"
    dhw_dis = dhw_disable(dhw_disable_bit, start, end)

    logging.getLogger("dhw_disable").setLevel(logging.DEBUG)
    logging.getLogger("in_window").setLevel(logging.INFO)

#    dhw_dis.set_dhw_enable()

    dhw_dis.check_dhw(True)
    time.sleep(1)

    print("set disable on")
    dhw_dis.set_dhw_enable()

    print("check with pump_running False")
    dhw_dis.check_dhw(False)
    time.sleep(1)

    print("check with pump_running True")
    dhw_dis.check_dhw(True)
    time.sleep(1)

    for ii in range(0,6):
        dhw_dis.report_dhw()
        dhw_dis.check_dhw(False)
        time.sleep(30)

    
    GPIO.cleanup()
