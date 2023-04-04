from enum import Enum
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from croniter import croniter

from schedule.schedule_util import calculate_cron_unit


class ScheduleTaskFailurePolicy(str, Enum):
    IGNORE = "ignore"
    RETRY = "retry"
    RETRY_DLQ = "retry_dlq"


class ScheduleTaskStatus:
    IDLE = "idle"
    WAITING = "waiting"
    RETRY = "retry"
    DONE = "done"
    FAILED = "failed"


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
            cron_elements = (
                schedule_event["schedule"].split()
                if type(schedule_event["schedule"]) is str
                else str(schedule_event["schedule"]).split()
            )
            next_time = None
            delay = 0
            if len(cron_elements) == 5:
                iter = croniter(schedule_event["schedule"], base)
                next_time = datetime.timestamp(iter.get_next(datetime))
                delay = next_time - datetime.timestamp(base)
            elif len(cron_elements) == 6:
                schedule_data = " ".join(cron_elements[1:])
                iter = croniter(schedule_data, base)
                next_time = datetime.timestamp(iter.get_next(datetime))
                secs = calculate_cron_unit(cron_elements[0])
                delay = next_time - datetime.timestamp(base) + secs
            else:
                raise Exception(f'wrong format error: {schedule_event["schedule"]}')
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
