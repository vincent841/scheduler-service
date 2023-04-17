from unittest import TestCase, main

from datetime import datetime
from schedule.schedule_cron import CronTime


class ScheduleCronTest(TestCase):

    """
    DIGITS TEST

    """

    def test_no_exceptions_1(self):
        try:
            CronTime("* * * * * *")
            CronTime("0 * * * * *")
            CronTime("08 * * * * *")
            CronTime("08 8 8 8 8 5")
            CronTime("* * * * *")
            CronTime("0-10 * * * * *")
            CronTime("0-10 0-10 * * * *")
            CronTime("0-10 0-10 1-10 1-10 0-6 0-1")
            CronTime("0,10 0,10 * * * *")
            CronTime("0,10 0,10 1,10 1,10 0,6 0,1")
        except Exception as ex:
            self.fail(f"test_no_exceptions_1 raised Exception: {ex}")

    def test_no_exceptions_2(self):
        try:
            CronTime("* * * * jan *")
            CronTime("* * * * jan,feb *")

        except Exception as ex:
            self.fail(f"test_no_exceptions_2 raised Exception: {ex}")

    """
    COMPARISON TEST
    
    """

    def test_standard_cron_format(self):
        standard = CronTime("8 8 8 8 5", "Asia/Seoul", None)
        extended = CronTime("0 8 8 8 8 5", "Asia/Seoul", None)

        self.assertEqual(standard.time_units, extended.time_units)

    """
    GET NEXT
    
    """

    def test_get_next_1(self):
        cron_time = CronTime("0 * * * * *", "Asia/Seoul", None)
        next_datetime = cron_time.get_next(datetime(2018, 6, 3, 0, 0), "Asia/Seoul")
        self.assertEqual(next_datetime.year, 2018)
        self.assertEqual(next_datetime.month, 6)
        self.assertEqual(next_datetime.day, 3)
        self.assertEqual(next_datetime.hour, 0)
        self.assertEqual(next_datetime.minute, 1)
        self.assertEqual(next_datetime.second, 0)

    def test_get_next_2(self):
        cron_time = CronTime("0 0 */4 * * *", "Asia/Seoul", None)
        next_datetime = cron_time.get_next(datetime(2018, 6, 3, 0, 0), "Asia/Seoul")
        self.assertEqual(next_datetime.year, 2018)
        self.assertEqual(next_datetime.month, 6)
        self.assertEqual(next_datetime.day, 3)
        self.assertEqual(next_datetime.hour, 4)
        self.assertEqual(next_datetime.minute, 0)
        self.assertEqual(next_datetime.second, 0)

    def test_get_next_3(self):
        base = datetime.fromisoformat("2018-03-29T23:15")

        cron_time = CronTime("30 0 * * 5", "Asia/Amman", None)
        next_datetime = cron_time.get_next(base, "Asia/Amman")
        print(next_datetime)
        self.assertEqual(next_datetime.year, 2018)
        self.assertEqual(next_datetime.month, 3)
        self.assertEqual(next_datetime.day, 30)
        self.assertEqual(next_datetime.hour, 1)
        self.assertEqual(next_datetime.minute, 0)
        self.assertEqual(next_datetime.second, 0)

        base = next_datetime
        next_datetime = cron_time.get_next(base, "Asia/Amman")
        self.assertEqual(next_datetime.year, 2018)
        self.assertEqual(next_datetime.month, 4)
        self.assertEqual(next_datetime.day, 6)
        self.assertEqual(next_datetime.hour, 0)
        self.assertEqual(next_datetime.minute, 30)
        self.assertEqual(next_datetime.second, 0)

        base = next_datetime
        next_datetime = cron_time.get_next(base, "Asia/Amman")
        self.assertEqual(next_datetime.year, 2018)
        self.assertEqual(next_datetime.month, 4)
        self.assertEqual(next_datetime.day, 13)
        self.assertEqual(next_datetime.hour, 0)
        self.assertEqual(next_datetime.minute, 30)
        self.assertEqual(next_datetime.second, 0)


if __name__ == "__main__":
    main()
