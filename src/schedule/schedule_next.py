from datetime import datetime
from croniter import croniter


class ScheduleEventNext:
    @staticmethod
    def get_next_and_delay(event, input_next_time=None):
        if event["type"] == "cron":
            base = datetime.now()
            iter = croniter(event["schedule"], base)
            next_time = datetime.timestamp(iter.get_next(datetime))
            delay = next_time - datetime.timestamp(base)
            next_time = int(next_time)
        elif event["type"] == "delay":
            base = datetime.now()
            next_time = datetime.timestamp(base) + int(event["schedule"])
            delay = next_time - datetime.timestamp(base)
            next_time = int(next_time)
        return (next_time, delay)
