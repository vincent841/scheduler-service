from typing import Union
from fastapi import FastAPI

from api.api_registration import process_registration, ANSRegistration


fast_api = FastAPI(
    title="Alarm Notification Service API",
    description="This service registers schedule information and manages registered schedules.",
)


@fast_api.post("/register")
async def register(input_params: ANSRegistration):
    return process_registration(input_params.dict())
