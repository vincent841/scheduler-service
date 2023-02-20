from typing import Union
from fastapi import FastAPI

from api.api_register import api_register
from schedule.schedule_register import ScheduleEvent


fast_api = FastAPI(
    title="Schedule Notification Service API",
    description="This service registers schedule information and manages registered schedules.",
)


@fast_api.post("/register")
async def register(input_params: ScheduleEvent):
    return api_register(input_params.dict())
