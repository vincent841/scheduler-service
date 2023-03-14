from pydantic import BaseModel
from typing import Optional
from enum import Enum


"""
Schedule Interface Definitions

"""


class ScheduleTaskFailurePolicy(str, Enum):
    IGNORE = "ignore"
    RETRY = "retry"
    RETRY_DLQ = "retry_dlq"


class ScheduleTask(BaseModel):
    type: str
    connection: dict
    data: dict
    history_check: Optional[bool] = False
    failed_policy: Optional[
        ScheduleTaskFailurePolicy
    ] = ScheduleTaskFailurePolicy.IGNORE
    max_retry_count: Optional[int] = 3


class ScheduleRegistration(BaseModel):
    name: str
    type: str
    schedule: str
    task: ScheduleTask


class ScheduleUnregistration(BaseModel):
    name: str


class ScheduleList(BaseModel):
    dlq: bool
