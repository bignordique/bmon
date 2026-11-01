
from time import time, sleep
import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from pathlib import Path
import re
import RPi.GPIO as GPIO
import argparse
import asyncio
from contextlib import suppress

TRUST_TEMP_WINDOW = 5*60 #seconds

class boiler_fan ():

    def __init__ (self, name, logger, temps_file, temp_target=75, loop_delay=60, hysteresis=1):
        self.logger = logger
        self.temps_file= temps_file
        self.temp_target = float(temp_target)
        self.loop_delay = int(loop_delay)
        self.hysteresis = hysteresis

        self.logger.info (f'{name} initialized\n')
        self.temp_line_re = re.compile(r'([+-]?\d+\.\d+|unk)')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(12,GPIO.OUT)

    async def run(self):
        temps_path = Path(self.temps_file)
        GPIO.output(12, GPIO.LOW)
        last_output = GPIO.LOW
        while True:
            fan_value = None
            wine_cellar = None  # for logging statements
            outside_air = None  # for logging statements

            if temps_path.is_file() and os.access(temps_path, os.R_OK):
                with open(temps_path, 'r', encoding='utf-8') as f:
                    last_line = f.readlines()[-1]

                groups = self.temp_line_re.findall(last_line)

                if len(groups) == 9:
                    current_time = time()
                    if current_time - float(groups[0])  < TRUST_TEMP_WINDOW:
                        outside_air = None if groups[1] == "unk" else float(groups[1])
                        wine_cellar = None if groups[2] == "unk" else float(groups[2])
                        if outside_air is not None and wine_cellar is not None:
                            diff_wine_temp = wine_cellar - self.temp_target
                            diff_outside_temp = wine_cellar - outside_air
                            if diff_wine_temp > self.hysteresis and diff_outside_temp > self.hysteresis:
                                fan_value = GPIO.HIGH
                            elif diff_wine_temp < -self.hysteresis or diff_outside_temp < -self.hysteresis:
                                fan_value = GPIO.LOW
                            else:
                                fan_value = GPIO.input(12)
                        else:
                            self.logger.warning((f'unk observed, outside_air: {groups[1]} wine_cellar: {groups[2]}.\n'))  
                    else:
                        self.logger.warning((f'Current - last temp time > {TRUST_TEMP_WINDOW}.\n'))
                else:
                    self.logger.warning((f'Extracted last line length not equal to 9 temps.\n  Last temp line: {groups}\n'))
            else:
                self.logger.warning((f'Temps file non existent, or non readable.\n'))

            if fan_value is None:
                GPIO.output(12, GPIO.LOW)
            else:
                GPIO.output(12, fan_value)

            if GPIO.input(12) != last_output:
                self.logger.info(f'fan control: {GPIO.input(12)}')

            last_output = GPIO.input(12)

            self.logger.debug(f'Fan control: {GPIO.input(12)}  target:{self.temp_target} wine_cellar:{wine_cellar} outside:{outside_air} ')
                
            await asyncio.sleep(self.loop_delay)


if __name__ == "__main__":

    name = "boiler_fan"

    parser = argparse.ArgumentParser(description="Read temps file and control a fan.")
    parser.add_argument("-tt", "--target_temp", default = 75, type = int, help="First argument must be target temperature.")
    parser.add_argument("-t", "--test", action="store_true", help="Perform test/verification procedure")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-l", "--loop_delay", default = 60, type=int, help="Seconds between temperature evaluations.")
    parser.add_argument("--hysteresis", default = 1, type=int, help="Determines width of deadband.")
    args = parser.parse_args()

    if args.test:

        test_dir="test/boiler_fan"
        log_file = test_dir+"/logfile"

        for path in Path(test_dir).glob("logfile*"):
            if path.is_file():
                path.unlink()

        for path in Path(test_dir).glob("temps*"):
            if path.is_file():
                path.unlink()

        test_handler = logging.StreamHandler(sys.stderr)
        test_formatter = logging.Formatter("%(asctime)s %(lineno)d: %(message)s")
        test_handler.setFormatter(test_formatter)
        test_handler.setLevel(logging.DEBUG)
        handlers=[test_handler]

        temps_file = test_dir+"/temps"

    else:
        log_file = "/srv/boiler_fan/logfile" 
        temps_file = "/srv/temps/data/temps"
        handlers = []

    formatter = logging.Formatter("%(asctime)s %(name)s %(module)s:%(lineno)d %(levelname)s:\n    %(message)s\n")
    rot_handler = RotatingFileHandler(log_file, maxBytes=30000, backupCount=5)
    rot_handler.setFormatter(formatter)
    if args.verbose:
        rot_handler.setLevel(logging.DEBUG)
    else:
        rot_handler.setLevel(logging.INFO)
    handlers += [rot_handler]

    logger = logging.getLogger(name)

    logging.basicConfig(handlers=handlers, level=logging.DEBUG) 

    async def gen_temps():
        # Assumes target temp is 75
        await asyncio.sleep(2*args.loop_delay)
        logger.debug("Should say temps file missing.\n")

        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " 57.1 83.4 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(1.1*args.loop_delay)
        logger.debug(f'wine_caav == 83.4, fan control is: {GPIO.input(12)} should be 1.')

        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " 57.1 74.1 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(1.1*args.loop_delay)
        logger.debug(f'wine_caav == 74.1, fan control is: {GPIO.input(12)} should be 1.')

        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " 57.1 73.9 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(1.1*args.loop_delay)
        logger.debug(f'wine_caav == 73.9, fan control is: {GPIO.input(12)} should be 0.')

        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " 57.1 75.9 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(1.1*args.loop_delay)
        logger.debug(f'wine_caav == 75.9, fan control is: {GPIO.input(12)} should be 0.')

        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " 57.1 76.1 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(1.1*args.loop_delay)
        logger.debug(f'wine_caav == 76.1, fan control is: {GPIO.input(12)} should be 1.')

        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " 77.0 76.1 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(1.1*args.loop_delay)
        logger.debug(f'outside_air == 77.0, fan control is: {GPIO.input(12)} should be 1.')

        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " 77.2 76.1 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(1.1*args.loop_delay)
        logger.debug(f'outside_air == 77.2, fan control is: {GPIO.input(12)} should be 0.')

        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " 75.2 76.1 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(1.1*args.loop_delay)
        logger.debug(f'outside_air == 75.2, fan control is: {GPIO.input(12)} should be 0.')

        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " 75.0 76.1 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(1.1*args.loop_delay)
        logger.debug(f'outside_air == 75.0, fan control is: {GPIO.input(12)} should be 1.')


        await asyncio.sleep(2*args.loop_delay)
        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " 83.4 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(args.loop_delay)
        logger.debug("Should say less than 9 entries on last line of temps.\n")

        await asyncio.sleep(2*args.loop_delay)
        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()-TRUST_TEMP_WINDOW-1) + " 57.1 83.4 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(args.loop_delay)
        logger.debug("Should say last temp > window.\n")

        await asyncio.sleep(2*args.loop_delay)
        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " unk 83.4 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(args.loop_delay)
        logger.debug("Shoud say unk error.\n")

        with open (temps_file, "a", encoding="utf-8") as f:
            f.write(str(time()) + " 57.1 61.1 61.1 153.2 151.0 113.6 109.6 104.0"+"\n")
        await asyncio.sleep(1.1*args.loop_delay)
        logger.debug(f'wine_caav == 61.1, fan control is: {GPIO.input(12)} should be 0.\n')


    bf = boiler_fan(name, logger, temps_file, args.target_temp, args.loop_delay, args.hysteresis)

    task_list = [bf.run()]
    if args.test: task_list += [gen_temps()]

    tasks = asyncio.gather(*task_list)

    loop = asyncio.get_event_loop()

    try:
        loop.set_debug(False)
        loop.run_until_complete(tasks)
    except KeyboardInterrupt as e:
        tasks.cancel()
        with suppress(asyncio.CancelledError):
            loop.run_until_complete(tasks)
        tasks.exception()
    finally:
        loop.close()

    GPIO.cleanup()
