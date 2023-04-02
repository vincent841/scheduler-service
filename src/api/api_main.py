from fastapi import FastAPI
from typing import Optional

from api.api_method import (
    api_register,
    api_delete_schedules,
    api_get_schedules,
    api_reset,
    api_get_groups,
    api_delete_schedule,
)

from api.api_interface import ScheduleRegistration
from schedule.schedule_event_handler import ScheduleEventHandler


fast_api = FastAPI(
    title="Scheduler Service API",
    description="This service registers schedule information and manages registered schedules.",
    contact={
        "name": "hatiolab",
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
async def register_schedule(inputs: ScheduleRegistration) -> dict:
    """
    register a schedule event
    """
    return api_register(inputs.dict())


@fast_api.delete("/schedules/{resp_id}")
async def delete_schedule(resp_id: str) -> dict:
    """
    unregister a schedule event
    """
    return api_delete_schedules(resp_id)


@fast_api.get("/schedules")
async def get_schedules() -> dict:
    """
    list all registered events
    """
    return api_get_schedules(None)


@fast_api.get("/schedules/{resp_id}")
async def get_schedules_with_resp_id(resp_id: str) -> dict or list:
    """
    list all registered events
    """
    return api_get_schedules(resp_id)


@fast_api.get("/failed-schedules")
async def get_failed_schedules() -> dict or list:
    """
    fetch all failed schedules
    """
    return api_get_schedules(None, "", "", True)


@fast_api.get("/schedule-groups")
async def get_schedule_groups() -> dict or list:
    return api_get_groups()


@fast_api.get("/schedule-groups/{group_id}")
async def get_schedule_group(group_id: str) -> dict or list:
    return api_get_schedules(None, group=group_id)


@fast_api.delete("/schedule-groups/{group_id}")
async def delete_schedule_group(group_id: str) -> dict or list:
    return api_delete_schedule(None, group=group_id)


@fast_api.post("/admin/reset")
async def reset() -> dict:
    """
    reset all queues
    """
    return api_reset()
