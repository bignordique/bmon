#!/var/www/html/python3_11/bin/python3.11
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
        self.logger = logging.getLogger(__name__)

    def check_entry(self):
        previous = self.next
        self.next= self.entry.next(datetime.datetime.now(tz=self.local_zone))
#        self.logger.debug(f'\n    {self.id}: previous: {previous}  next: {self.next}\n')
        if self.next > previous:
            self.func()


if __name__ == "__main__":

    def print_time():
        print(datetime.datetime.now())

    import time

    logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s:%(message)s', 
                        level=logging.DEBUG)

    a = cron_entry("cron_entry_test", "*/1 * * * *", print_time)
    logging.getLogger('__main__').setLevel(logging.INFO)

    for ii in range(0,10):
        a.check_entry()
        time.sleep(2)
    
