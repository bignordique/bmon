#!/home/pi/bmon/venv/bin/python

# Only enable dhw_disable on the positive edge of is_night.   If dhw_disable is
# disabled in the middle of is_night, it won't enable until the next
# positive edge of is_night.

# Some thought of resetting the pump_running file at the transition
# from was_night to not is_night.  Could end up with pump_running TRUE or
# FALSE.   If TRUE, then dhw_disable is disabled.   If stuck FALSE, then
# the pump_running overide is disabled.   Which as long as the pump disable
# only works during the night, shouldn't be very noticable.  Simplify and
# don't reset pump_running.

import asyncio
import RPi.GPIO as GPIO
from in_window import in_window
import logging

class dhw_disable ():

    def __init__ (self, name, bit):
        self.name = name
        self.bit = bit
        GPIO.setup(bit, GPIO.OUT)
        GPIO.output(bit, GPIO.LOW)
        self.pump_status_file = "/tmp/pump_status"
        self.night_window = in_window("night_window",\
                                      "0-59/30 0 * * *", "15-59/30 4 * * *")
#                                      "0-59/30 * * * *", "15-59/30 * * * *")
#                                      "0-58/2  * * * *", "1-59/2  * * * *")
        self.logger = logging.getLogger(__name__)
        self.logger.info(f' startup')

    def set_dhw_disable(self):
        if GPIO.input(self.bit) == GPIO.LOW :
            GPIO.output(self.bit, GPIO.HIGH)
            self.report_dhw()

    def set_dhw_enable(self):
        if GPIO.input(self.bit) == GPIO.HIGH :
            GPIO.output(self.bit, GPIO.LOW)
            self.report_dhw()

    def report_dhw (self):
        self.logger.debug(f'\n    {GPIO.input(self.bit)}\n')

    async def loop(self):
        was_night = self.night_window.check()
        while True:
            pump_status = ""
            try :
                with open(self.pump_status_file, "r") as f: 
                    pump_status = f.read()
            except : pass

            is_night = self.night_window.check()
            
            pump_running = pump_status == "running"
            was_gpio = GPIO.input(self.bit)

            if is_night and not was_night and not pump_running :
                self.set_dhw_disable()
            if not is_night or pump_running : 
                self.set_dhw_enable()

            self.logger.log(5, f'\n    pump_running: {pump_running}' + \
                               f'  is_night: {is_night}' + \
                               f'  was_night: {was_night}' + \
                               f'  bit: {GPIO.input(self.bit)}\n')

            await asyncio.sleep(1)
            was_night = is_night

if __name__ == "__main__":

    from contextlib import suppress

    dhw_disable_bit = 18

    logging.basicConfig(format="%(asctime)s %(name)s %(module)s:%(lineno)d " + \
                               "%(levelname)s:%(message)s")

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    dhw_dis = dhw_disable("dhw_disable", dhw_disable_bit)

    logging.getLogger(__name__).setLevel(logging.DEBUG)
#    logging.getLogger(__name__).setLevel(5)
    logging.getLogger("in_window").setLevel(logging.INFO)

    tasks = asyncio.gather(
        asyncio.ensure_future(dhw_dis.loop())
    )

    loop = asyncio.get_event_loop()

    try:
        loop.set_debug(False)
        loop.run_until_complete(tasks)
    except KeyboardInterrupt as e:
        print (f'keyboardinterrupt: {e}')
        tasks.cancel()
        with suppress(asyncio.CancelledError):
            loop.run_until_complete(tasks)
        tasks.exception()
    finally:
        loop.close()

    dhw_dis.set_dhw_enable()
    GPIO.cleanup()
