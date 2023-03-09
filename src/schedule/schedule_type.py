from pydantic import BaseModel
from enum import Enum


"""
Schedule Interface Definitions

"""


class ScheduleTask(BaseModel):
    type: str
    connection: dict
    data: dict


class ScheduleRegistration(BaseModel):
    name: str
    type: str
    schedule: str
    task: ScheduleTask


class ScheduleUnregistration(BaseModel):
    name: str


"""
Schedule Event

"""


class ScheduleEventType(Enum):
    CRON = "cron"
    NOW = "now"
    DELAY = "delay"
    DELAY_RECUR = "delay-recur"
    DATE = "date"
