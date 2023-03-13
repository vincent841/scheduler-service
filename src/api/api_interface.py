from pydantic import BaseModel


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


class ScheduleList(BaseModel):
    dlq: bool
