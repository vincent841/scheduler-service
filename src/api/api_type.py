from pydantic import BaseModel


class ENSRegistrationData(BaseModel):
    name: str
    type: str
    schedule: str
    data: dict


class ENSRegistrationResult(BaseModel):
    name: str
    type: str
    schedule: str
    data: dict
    result: dict
