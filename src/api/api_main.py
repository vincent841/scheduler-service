from fastapi import FastAPI

from api.api_register import api_register
from api.api_unregister import api_unregister
from api.api_list import api_list

from schedule.schedule_type import (
    ScheduleRegistration,
    ScheduleUnregistration,
)
from schedule.schedule_event_handler import ScheduleEventHandler


fast_api = FastAPI(
    title="Scheduler Service API",
    description="This service registers schedule information and manages registered schedules.",
)


@fast_api.on_event("startup")
async def startup_event():
    schedule_handler = ScheduleEventHandler()
    schedule_handler.initialize()


@fast_api.on_event("shutdown")
async def shutdown_event():
    pass


@fast_api.post("/register")
async def register(input_params: ScheduleRegistration) -> dict:
    """
    register a schedule event
    """
    return api_register(input_params.dict())


@fast_api.post("/unregister")
async def unregister(input_params: ScheduleUnregistration) -> dict:
    """
    unregister a schedule event
    """
    return api_unregister(input_params.dict())


@fast_api.post("/list")
async def list() -> dict:
    """
    list all registered events
    """
    return api_list()
