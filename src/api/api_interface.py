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


class ScheduleClient(BaseModel):
    operation: str
    application: Optional[str]
    group: Optional[str]
    key: Optional[str]
    type: Optional[str]


class ScheduleTask(BaseModel):
    type: str
    connection: dict
    data: dict
    history_check: Optional[bool] = False
    failed_policy: Optional[
        ScheduleTaskFailurePolicy
    ] = ScheduleTaskFailurePolicy.IGNORE
    max_retry_count: Optional[int] = 3
    retry_period: Optional[int] = 60


class Schedule(BaseModel):
    name: str
    client: ScheduleClient
    type: str
    schedule: str
    timezone: str
    task: ScheduleTask


class ScheduleAdmin(BaseModel):
    user: str
    password: str
