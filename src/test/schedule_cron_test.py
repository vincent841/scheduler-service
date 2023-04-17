from unittest import TestCase, main

from datetime import datetime
from schedule.schedule_cron import CronTime


class ScheduleCronTest(TestCase):
    def get_next_test(self):
        cron_time = CronTime("0 * * * * *", "Asia/Seoul", None)
        next_datetime = cron_time.get_next(datetime(2018, 6, 3, 0, 0), "Asia/Seoul")
        print(next_datetime)


if __name__ == "__main__":
    main()
