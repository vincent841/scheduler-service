from fastapi import FastAPI

from api.api_register import api_register
from api.api_unregister import api_unregister
from api.api_list import api_list

from api.api_interface import ScheduleRegistration, ScheduleUnregistration, ScheduleList
from schedule.schedule_event_handler import ScheduleEventHandler


fast_api = FastAPI(
    title="Scheduler Service API",
    description="This service registers schedule information and manages registered schedules.",
    contact={
        "name": "jinwon",
        "url": "https://www.hatiolab.com",
        "email": "jinwon@hatiolab.com",
    },
)


@fast_api.on_event("startup")
async def startup_event():
    schedule_handler = ScheduleEventHandler()
    schedule_handler.initialize()


@fast_api.on_event("shutdown")
async def shutdown_event():
    pass


@fast_api.post("/register")
async def register(inputs: ScheduleRegistration) -> dict:
    """
    register a schedule event
    """
    return api_register(inputs.dict())


@fast_api.post("/unregister")
async def unregister(inputs: ScheduleUnregistration) -> dict:
    """
    unregister a schedule event
    """
    return api_unregister(inputs.dict())


@fast_api.post("/list")
async def list(inputs: ScheduleList) -> dict:
    """
    list all registered events
    """
    return api_list(inputs.dict())
