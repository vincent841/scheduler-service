import strawberry
from strawberry.scalars import JSON
from enum import Enum
from typing import Optional, List
from dataclasses_json import dataclass_json

from schedule.schedule_event_handler import ScheduleEventHandler

import traceback
import sys
from helper.logger import Logger

log_message = Logger.get("gql_types", Logger.Level.INFO, sys.stdout)

log_debug = log_message.debug
log_info = log_message.info
log_warning = log_message.warning
log_error = log_message.error


"""
****************************************************************************************************************
Type Declaration
****************************************************************************************************************
"""


@strawberry.enum
class ScheduleTaskFailurePolicy(Enum):
    IGNORE = "ignore"
    RETRY = "retry"
    RETRY_DLQ = "retry_dlq"


@strawberry.input
class TaskConnectionInput:
    host: str
    topic: Optional[str] = ""
    headers: Optional[JSON]


@strawberry.input
class ScheduleTaskInput:
    type: str
    connection: TaskConnectionInput
    data: JSON
    history_check: Optional[bool] = False
    failed_policy: Optional[
        ScheduleTaskFailurePolicy
    ] = ScheduleTaskFailurePolicy.IGNORE
    max_retry_count: Optional[int] = 3


@dataclass_json
@strawberry.input
class ScheduleEventInput:
    name: str
    type: str
    schedule: str
    task: ScheduleTaskInput


@dataclass_json
@strawberry.type
class RegisteredEvent:
    name: str
    resp_id: str


@strawberry.enum
class ScheduleTaskStatus(Enum):
    IDLE = "idle"
    WAITING = "waiting"
    RETRY = "retry"
    DONE = "done"
    FAILED = "failed"


@dataclass_json
@strawberry.type
class TaskConnection:
    host: str
    topic: Optional[str] = ""
    headers: Optional[JSON]


@dataclass_json
@strawberry.type
class ScheduleTask:
    type: str
    connection: TaskConnection
    data: JSON
    history_check: Optional[bool] = False
    failed_policy: Optional[
        ScheduleTaskFailurePolicy
    ] = ScheduleTaskFailurePolicy.IGNORE
    max_retry_count: Optional[int] = 3
    status: Optional[ScheduleTaskStatus] = ScheduleTaskStatus.IDLE
    iteration: Optional[int] = 0
    last_run: Optional[str] = ""
    retry_count: Optional[int] = 0


@dataclass_json
@strawberry.type
class ScheduleEvent:
    name: str
    type: str
    schedule: str
    task: ScheduleTask


@dataclass_json
@strawberry.input
class QueueTypeInput:
    dlq: bool
