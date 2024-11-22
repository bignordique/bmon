#!/home/pi/bmon/venv/bin/python

import asyncio
import RPi.GPIO as GPIO
from datetime import datetime
from time import time
from contextlib import suppress
import logging

class gpio_filter ():

    pos_wait = 1
    neg_wait = 2
    edge_trigger_threshold = 30
    time_format = "%x %X"

    def __init__ (self, name, bit, zc_logger):
        self.name = name
        self.bit = bit
        self.zc_logger = zc_logger
        GPIO.setup(bit, GPIO.IN)
        GPIO.add_event_detect(bit, GPIO.RISING)
        GPIO.add_event_callback(bit, self.set_seen)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.last_time = time()
        self.edges_seen = 0
        self.value = 0
        self.logger.info(f'{self.name} startup')
        self.write_log("startup")

    def set_seen(self, channel):
        now_time = time()
        diff_time = now_time - self.last_time
        self.edges_seen += 1  
        self.logger.debug (f'{self.name} {diff_time:.4f} {self.edges_seen}')
        self.last_time = now_time


    def write_log_posedge(self, edges_seen):
        self.zc_logger.info(f'{time()} {self.name} 1 {edges_seen}')

    def write_log(self, status):
        self.zc_logger.info(f'{time()} {self.name} 0 {status}')

    async def pos_edge(self):
        self.wait_task = asyncio.create_task(self.wait_cycle(0))  # create fake wait task
        while True:
            await asyncio.sleep(self.pos_wait)
            if self.edges_seen > 0:
                if self.edges_seen > self.edge_trigger_threshold:
                    if not self.wait_task.done():
                        self.wait_task.cancel()
                    if self.value == 0:
                        self.value = 1
                        self.write_log_posedge(self.edges_seen)
                    self.wait_task = asyncio.create_task(self.wait_cycle(self.neg_wait))
                self.edges_seen = 0

    async def wait_cycle(self, wait_time):
        if wait_time != 0:
            await asyncio.sleep(wait_time)
            self.value = 0
            self.write_log("")

    def kill_wait_cycle(self):
        if not self.wait_task.done():
            self.wait_task.cancel()

if __name__ == "__main__":

    logging.basicConfig(format="%(asctime)s %(name)s %(module)s:%(lineno)d %(levelname)s:%(message)s",
            level=logging.INFO)

    GPIO.setmode(GPIO.BCM)
    filt = gpio_filter("lower_lake", 4, "test_log")
    tasks = asyncio.gather(
        asyncio.ensure_future(filt.pos_edge())
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

    GPIO.cleanup()
