from datetime import datetime
from croniter import croniter


class ScheduleEventNext:
    @staticmethod
    def process_next(event):
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
