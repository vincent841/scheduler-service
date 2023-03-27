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


"""
****************************************************************************************************************
utils
****************************************************************************************************************
"""


def convert_schevent_to_dict(schevent: ScheduleEventInput) -> dict:
    schevent_dict = schevent.to_dict()
    schedule_task = schevent_dict["task"]
    failed_policy = schedule_task.get("failed_policy", ScheduleTaskFailurePolicy.IGNORE)
    schedule_task["failed_policy"] = failed_policy.value
    status = schedule_task.get("status", ScheduleTaskStatus.IDLE)
    schedule_task["status"] = status.value
    return schevent_dict


def covent_dict_to_schevent(schevent_dict: dict) -> ScheduleEvent:
    if schevent_dict == {}:
        return None

    schevent = ScheduleEvent.from_dict(schevent_dict)
    schevent.task.failed_policy = ScheduleTaskFailurePolicy(schevent.task.failed_policy)
    schevent.task.status = ScheduleTaskStatus(schevent.task.status)
    return schevent


"""
****************************************************************************************************************
Mutation
****************************************************************************************************************
"""


@strawberry.type
class Mutation:
    @strawberry.mutation
    def register_schedule(self, registration: ScheduleEventInput) -> RegisteredEvent:
        req_schedule = convert_schevent_to_dict(registration)
        schedule_register = ScheduleEventHandler()
        result = schedule_register.register(req_schedule)

        # return RegisteredEvent(name=result["name"], resp_id=result["resp_id"])
        return RegisteredEvent.from_dict(result)

    @strawberry.mutation
    def unregister_schedule(self, schedule_name: str) -> RegisteredEvent:
        schedule_register = ScheduleEventHandler()
        result = schedule_register.unregister(schedule_name)
        return RegisteredEvent.from_dict(result)


"""
****************************************************************************************************************
Query
****************************************************************************************************************
"""


@strawberry.type
class Query:
    @strawberry.field
    def scheduled_list(self, queue_type: QueueTypeInput) -> List[ScheduleEvent]:
        queue_type_dict = queue_type.to_dict()

        schedule_handler = ScheduleEventHandler()
        result_list = schedule_handler.list(queue_type_dict)

        scheduled_event_list = list()
        for result in result_list:
            scheduled_event_list.append(covent_dict_to_schevent(result))

        return scheduled_event_list
