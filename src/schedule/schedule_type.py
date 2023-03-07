from pydantic import BaseModel


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
