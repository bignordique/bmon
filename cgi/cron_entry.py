#!/home/pi/bmon/venv/bin/python

# This one is for threads, not asyncio  Call check entry and the func will be
# called when appropriate.   The other version used asyncio and
# had a private timer loop.  Once launched, would call the func
# on its own.   Unfortuneately, same names were used.   "pip install crontab" required.
import logging
import datetime
from dateutil import tz
import pytz
from crontab import CronTab

"""  One shots cron jobs """

class cron_entry():

    def __init__(self, id, tab, func):
        self.id = id
        self.entry = CronTab(tab)
        self.func = func
        self.local_zone = tz.tzlocal()
        self.next = self.entry.next(datetime.datetime.now(tz=self.local_zone))
        self.logger = logging.getLogger(id)

    def check_entry(self):
        previous = self.next
        self.next= self.entry.next(datetime.datetime.now(tz=self.local_zone))
        self.logger.debug(f'\n    previous: {previous}  next: {self.next}\n')
        if self.next > previous:
            self.func()


if __name__ == "__main__":

    def print_time():
        print(f'**** Cron activates {datetime.datetime.now()}\n')

    import time

    logging.basicConfig(format='%(asctime)s %(name)s %(module)s:%(lineno)d %(levelname)s:%(message)s', 
                        level=logging.DEBUG)

    a = cron_entry("cron_entry_test", "*/1 * * * *", print_time)
    logging.getLogger('__main__').setLevel(logging.INFO)

    for ii in range(0,10):
        a.check_entry()
        time.sleep(2)
    
