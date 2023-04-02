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
    application: str
    group: str
    key: str


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
    client: ScheduleClient
    type: str
    schedule: str
    task: ScheduleTask


class ScheduleRegistrationResult(BaseModel):
    client: ScheduleClient
    resp_id: str


class ScheduleList(BaseModel):
    dlq: bool = False
    application: str = ""
    group: str = ""
