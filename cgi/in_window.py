#!/home/pi/bmon/venv/bin/python
import logging
import datetime
from dateutil import tz
from crontab import CronTab

"""  One shots cron jobs """

class in_window():

    def __init__(self, id, start_tab, end_tab):
        self.id = id
        self.start_entry = CronTab(start_tab)
        self.end_entry = CronTab(end_tab)
        self.local_zone = tz.tzlocal()
        self.logger = logging.getLogger(__name__)

    def check(self):
        now_time = datetime.datetime.now(tz=self.local_zone)
        start = self.start_entry.next(now_time)
        end = self.end_entry.next(now_time)
        diff = start - end
        self.logger.debug(f'\n    start: {start}  end: {end} diff: {diff}\n')
        if diff > 0 : return True
        else: return False

if __name__ == "__main__":

    def print_time():
        print(f'**** Cron activates {datetime.datetime.now()}\n')

    import time

    logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s:%(message)s')

    a = in_window("in_window_test", "0-58/2 * * * *", "1-59/2 * * * *")
    logging.getLogger('__main__').setLevel(logging.DEBUG)

    for ii in range(0,1000):
        print(a.check())
        time.sleep(1)
    
