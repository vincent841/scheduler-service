from typing import Union
from fastapi import FastAPI

from api.api_register import api_register
from schedule.schedule_register import ScheduleEvent


fast_api = FastAPI(
    title="Schedule Notification Service API",
    description="This service registers schedule information and manages registered schedules.",
)


# TODO: will define the return dictionary format


@fast_api.post("/register")
async def register(input_params: ScheduleEvent) -> dict:
    return api_register(input_params.dict())


@fast_api.post("/unregister")
async def unregister(name: str) -> dict:
    return {"status": "ok"}


@fast_api.post("/update")
async def update(input_params: ScheduleEvent) -> dict:
    return {"status": "ok"}
