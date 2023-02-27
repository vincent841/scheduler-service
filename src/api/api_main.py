from typing import Union
from fastapi import FastAPI
from threading import Event

from config import Config
from api.api_register import api_register
from api.api_unregister import api_unregister

from schedule.schedule_loop import ScheduleEventLoop
from schedule.schedule_event_handler import ScheduleRegisterData, ScheduleUnregisterData


fast_api = FastAPI(
    title="Schedule Notification Service API",
    description="This service registers schedule information and manages registered schedules.",
)


# TODO: will define the return dictionary format
exit_event = Event()


@fast_api.on_event("startup")
async def startup_event():
    """
    event process loop as a thread
    """
    event_loop = ScheduleEventLoop(Config.evt_queue(), exit_event)
    event_loop.start()


@fast_api.on_event("shutdown")
async def shutdown_event():
    """
    exit the event process loop
    """
    exit_event.set()


@fast_api.post("/register")
async def register(input_params: ScheduleRegisterData) -> dict:
    return api_register(input_params.dict())


@fast_api.post("/unregister")
async def unregister(input_params: ScheduleUnregisterData) -> dict:
    return api_unregister(input_params.dict())


@fast_api.post("/update")
async def update(input_params: ScheduleRegisterData) -> dict:
    return {"status": "ok"}
