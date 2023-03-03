from datetime import datetime
from croniter import croniter


class ScheduleEventNext:
    @staticmethod
    def get_next(event):
        if event["type"] == "cron":
            base = datetime.now()
            iter = croniter(event["schedule"], base)
            next_time = iter.get_next(datetime)
            next_time = int(datetime.timestamp(next_time) * 1000000000)
        elif event["type"] == "delay":
            base = datetime.now()
            next_time = datetime.timestamp(base) + int(event["schedule"])
            next_time = int(next_time * 1000000000)

        return next_time

    @staticmethod
    def get_next_and_delay(event):
        if event["type"] == "cron":
            base = datetime.now()
            iter = croniter(event["schedule"], base)
            next_time = datetime.timestamp(iter.get_next(datetime))
            delay = next_time - datetime.timestamp(base)
            next_time = int(next_time * 1000000000)
        elif event["type"] == "delay":
            base = datetime.now()
            next_time = datetime.timestamp(base) + int(event["schedule"])
            delay = next_time - datetime.timestamp(base)
            next_time = int(next_time * 1000000000)

        return (next_time, delay)

    @staticmethod
    def get_delay(event):
        if event["type"] == "cron":
            base = datetime.now()
            iter = croniter(event["schedule"], base)
            next_time = iter.get_next(datetime)
            delay_time = next_time - datetime.timestamp(base)
            delay_time = int(datetime.timestamp(delay_time) * 1000000000)
        elif event["type"] == "delay":
            base = datetime.now()
            next_time = datetime.timestamp(base) + int(event["schedule"])
            delay_time = next_time - datetime.timestamp(base)
            delay_time = int(delay_time * 1000000000)

        return delay_time
