#!/home/pi/bmon/venv/bin/python

import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from w1thermsensor import W1ThermSensor, Sensor, Unit
import w1thermsensor.errors as w1sensorerrors
from contextlib import suppress
from time import time, sleep

temps_file = "/home/pi/bmon/data/t/temps"
logfile = "/home/pi/bmon/log/temps_logfile"
time_format = "%X"
rd_interval = 60

class rd_w1_temps ():

    def __init__ (self, name, temps_logger):
        self.name = name
        self.temps_logger = temps_logger
        self.logger = logging.getLogger(__name__)
        sensor_list = (("outside_air", "012292fae7bc"),
                       ("wine_caav", "0122931d5e9c"),
                       ("primary_inlet", "012275c43e73"),
                       ("hw_supply", "012275cc1dfe"),
                       ("hw_recirc", "012275d30826"),
                       ("floor", "012292e68553"))
        self.sensors = dict()
        for sensor in sensor_list:
            try:
                therm_sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=sensor[1])
                self.sensors[sensor[0]] = therm_sensor
            except w1thermsensor.errors.NoSensorFoundError:
                self.logging.error(f'Missing sensor: {sensor}')
            except Exception as e:
                self.logger.error(f'Missing {sensor}, cause: {repr(e)}') 

        for key,value in self.sensors.items():
            self.logger.info (f'{key}: {value}')

    def run(self):
        temps = ""
        while True:
            last_temps = temps
            temps = ""
            for sensor in self.sensors:
                if temps != "": temps += " "
                try:
                    temp = str(round(self.sensors[sensor].get_temperature(Unit.DEGREES_F), 1)) 
                except w1sensorerrors.SensorNotReadyError:
                    self.logger.error(f'{sensor} SensorNotReadyError')
                    temp = "unk"
                except w1sensorerrors.ResetValueError:
                    self.logger.error(f'{sensor} ResetValueError')
                    temp = "unk"
                except Exception as e:
                    self.logger.error(f'{sensor} unknown exception {repr(e)}')
                temps += temp
            if last_temps != temps:
                self.temps_logger.info(f'{time()} {temps}')
            sleep(rd_interval)


if __name__ == "__main__":
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    rot_handler = RotatingFileHandler(logfile, maxBytes=30000, backupCount=5)
    logging.basicConfig(format="%(asctime)s %(name)s %(module)s:%(lineno)d "+\
                               "%(levelname)s:\n    %(message)s\n",
                        handlers = [rot_handler],
                        level=logging.DEBUG) 

    temps_logger = logging.getLogger('temps_logger')
    temps_logger.propagate = False
    temps_rot_handler = \
        TimedRotatingFileHandler(temps_file, when='midnight', backupCount=7)
    temps_logger.addHandler(temps_rot_handler)
    temps_logger.setLevel(logging.INFO)

    rd_w1_temps_inst = rd_w1_temps("rd_w1_temps", temps_logger)

    rd_w1_temps_inst.run()
