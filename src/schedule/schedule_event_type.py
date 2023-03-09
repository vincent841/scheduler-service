from datetime import datetime
from croniter import croniter


class ScheduleEventType:
    NOW = "now"
    DELAY = "delay"
    DATE = "date"
    CRON = "cron"
    DELAY_RECUR = "delay-recur"

    @staticmethod
    def is_available_type(schedule_type):
        return schedule_type in [
            ScheduleEventType.CRON,
            ScheduleEventType.DELAY_RECUR,
            ScheduleEventType.NOW,
            ScheduleEventType.DELAY,
            ScheduleEventType.DATE,
        ]

    @staticmethod
    def is_recurring(schedule_type):
        return schedule_type in [ScheduleEventType.CRON, ScheduleEventType.DELAY_RECUR]

    @staticmethod
    def get_next_and_delay(schedule_event):
        base = datetime.now()
        if schedule_event["type"] == ScheduleEventType.CRON:
            iter = croniter(schedule_event["schedule"], base)
            next_time = datetime.timestamp(iter.get_next(datetime))
            delay = next_time - datetime.timestamp(base)
        elif (
            schedule_event["type"] == ScheduleEventType.DELAY_RECUR
            or schedule_event["type"] == ScheduleEventType.DELAY
        ):
            next_time = datetime.timestamp(base) + int(schedule_event["schedule"])
            delay = next_time - datetime.timestamp(base)
        elif schedule_event["type"] == ScheduleEventType.NOW:
            next_time = datetime.timestamp(base)
            delay = 0
        elif schedule_event["type"] == ScheduleEventType.DATE:
            next_time = datetime.fromisoformat(schedule_event["schedule"]).timestamp()
            delay = next_time - datetime.timestamp(base)
        else:
            raise Exception("Invalid schedule type")

        return (int(next_time), delay if delay >= 0 else 0)
