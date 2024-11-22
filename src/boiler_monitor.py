#!/home/pi/bmon/venv/bin/python

import asyncio
from gpio_filter import gpio_filter
from dhw_disable import dhw_disable
import logging
from logging.handlers import TimedRotatingFileHandler,RotatingFileHandler
import RPi.GPIO as GPIO
from contextlib import suppress

GPIO.setmode(GPIO.BCM)

zc_file = "/mnt/nfsshare/zone_change"
zc_logfile = "/home/pi/bmon/log/zc_logfile"
dhw_disable_bit = 18

class boiler_monitor ():

    def __init__ (self, zc_logger):
        self.lower_lake = gpio_filter("lower_lake", 4, zc_logger)
        self.lower_street = gpio_filter("lower_street", 17, zc_logger)
        self.shop = gpio_filter("shop", 27, zc_logger)
        self.upper_bedroom = gpio_filter("upper_family", 22, zc_logger)
        self.upper_hallway = gpio_filter("upper_hallway", 19, zc_logger)
        self.upper_family = gpio_filter("upper_bedroom", 26, zc_logger)
        self.hw_tank = gpio_filter("hw_tank", 6, zc_logger)
        self.boiler = gpio_filter("boiler", 5, zc_logger)
        self.dhw_disable = dhw_disable("dhw_disable", dhw_disable_bit)


if __name__ == "__main__":
    rot_handler = RotatingFileHandler(zc_logfile, maxBytes=30000, backupCount=5)
    logging.basicConfig(format=
        "%(asctime)s %(name)s %(module)s:%(lineno)d %(levelname)s:%(message)s",
        handlers = [rot_handler],
        level=logging.INFO)


    zc_logger = logging.getLogger('zc_logger')
    zc_logger.propagate = False
    zc_rot_handler = \
        TimedRotatingFileHandler(zc_file, when='midnight', backupCount=7)
    zc_logger.addHandler(zc_rot_handler)
    zc_logger.setLevel(logging.INFO)


    main = boiler_monitor(zc_logger)

#    logging.getLogger('gpio_filter').setLevel(logging.DEBUG)
    logging.getLogger('dhw_disable').setLevel(logging.DEBUG)

    tasks = asyncio.gather(
        asyncio.ensure_future(main.lower_lake.pos_edge()),
        asyncio.ensure_future(main.lower_street.pos_edge()),
        asyncio.ensure_future(main.shop.pos_edge()),
        asyncio.ensure_future(main.upper_bedroom.pos_edge()),
        asyncio.ensure_future(main.upper_hallway.pos_edge()),
        asyncio.ensure_future(main.upper_family.pos_edge()),
        asyncio.ensure_future(main.hw_tank.pos_edge()),
        asyncio.ensure_future(main.boiler.pos_edge()),
        asyncio.ensure_future(main.dhw_disable.loop())
    )

    loop = asyncio.get_event_loop()

    try:
        loop.set_debug(False)
        loop.run_until_complete(tasks)
    except KeyboardInterrupt as e:
        tasks.cancel()
# OK, I'm lazy
        main.lower_lake.kill_wait_cycle()
        main.lower_street.kill_wait_cycle()
        main.shop.kill_wait_cycle()
        main.upper_bedroom.kill_wait_cycle()
        main.upper_hallway.kill_wait_cycle()
        main.upper_family.kill_wait_cycle()
        main.hw_tank.kill_wait_cycle()
        main.boiler.kill_wait_cycle()
        with suppress(asyncio.CancelledError):
            loop.run_until_complete(tasks)
        tasks.exception()
    finally:
        loop.close()

    main.dhw_disable.set_enable_dhw()
    GPIO.cleanup()
