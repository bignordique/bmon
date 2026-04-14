#!/home/leith/bmon/.venv/bin/python

import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from w1thermsensor import W1ThermSensor, Sensor, Unit
from w1thermsensor import errors as W1thermsensorerrors
from contextlib import suppress
from time import time, sleep
import json

temps_file = "/srv/temps/data/temps"
logfile = "/srv/temps/temps_logfile"
RIGID_AC_TEMP_FILE = "/tmp/rigid_ac_temp"
RIGID_AC_POW_FILE = "/tmp/rigid_ac_pow"
time_format = "%X"
rd_interval = 60

class rd_w1_temps ():

    def __init__ (self, name, temps_logger):
        self.name = name
        self.temps_logger = temps_logger
        self.logger = logging.getLogger(__name__)
        sensor_list = (("outside_air", "012292fae7bc"),
                       ("wine_caav", "0122931d5e9c"),
                       ("rigid_ac_temp", RIGID_AC_TEMP_FILE),
                       ("rigid_ac_pow", RIGID_AC_POW_FILE),
                       ("primary_inlet", "012275c43e73"),
                       ("hw_supply", "012275cc1dfe"),
                       ("hw_recirc", "012275d30826"),
                       ("floor", "012292e68553"))
        self.sensors = dict()
        for sensor in sensor_list:
            if sensor[1] != RIGID_AC_TEMP_FILE and sensor[1] != RIGID_AC_POW_FILE:
                try:
                    therm_sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=sensor[1])
                    self.sensors[sensor[0]] = therm_sensor
                except W1thermsensorerrors.NoSensorFoundError:
                    self.logger.error(f'Missing sensor: {sensor}')
                except Exception as e:
                    self.logger.error(f'Missing {sensor}, cause: {repr(e)}') 
            else: 
                self.sensors[sensor[0]] = sensor[1]

        for key,value in self.sensors.items():
            self.logger.info (f'{key}: {value}')

    def run(self):
        temps = ""
        while True:
            last_temps = temps
            temps = ""
            for sensor in self.sensors:
                if temps != "": temps += " "
                if sensor != "rigid_ac_temp" and sensor != "rigid_ac_pow":
                    temp = "unk"
                    try:
                        temp = str(round(self.sensors[sensor].get_temperature(Unit.DEGREES_F), 1)) 
                    except W1thermsensorerrors.SensorNotReadyError:
                        self.logger.error(f'{sensor} SensorNotReadyError')
                    except W1thermsensorerrors.ResetValueError:
                        self.logger.error(f'{sensor} ResetValueError')
                    except Exception as e:
                        self.logger.error(f'{sensor} unknown exception {repr(e)}')
                else:
                    if sensor == "rigid_ac_temp":
                        try:
                            with open(RIGID_AC_TEMP_FILE, 'r') as f:
                                data = json.load(f)
                                temp = str(data["temp"])
                        except IOError as e:
                            print(e)
                            temp = "unk"
                    else:
                        try:
                            with open(RIGID_AC_POW_FILE, 'r') as f:
                                data = json.load(f)
                                temp = str(data["pow"])
                        except IOError as e:
                            print(e)
                            temp = "unk"
                temps += temp
            if last_temps != temps:
                self.temps_logger.info(f'{time()} {temps}')
            sleep(rd_interval)


if __name__ == "__main__":
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
