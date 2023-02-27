import json
from pydantic import BaseModel
from db.timestamp_db import TimestampDB

from config import Config
import uuid
from croniter import croniter
from datetime import datetime

from schedule.schedule_next import ScheduleEventNext


class ScheduleRegisterData(BaseModel):
    name: str
    type: str
    schedule: str
    data: str


class ScheduleUnregisterData(BaseModel):
    resp_id: str


class ScheduleEventHandler:
    def __init__(self):
        try:
            self.tdb = TimestampDB(Config.evt_queue())
        except Exception as ex:
            raise ex

    def register(self, input_data: dict) -> str:
        try:
            assert (
                input_data["name"]
                and input_data["type"]
                and input_data["schedule"]
                and input_data["data"]
            )

            # generate response id
            resp_id = uuid.uuid4()

            # store this input_data to timastamp db
            input_data["resp_id"] = str(resp_id)

            next_time = ScheduleEventNext.process_next(input_data)

            self.tdb.put(next_time, input_data)
            return str(resp_id)
        except Exception as ex:
            raise ex

    def unregister(self, input_data: dict):
        try:
            key_value_events = self.tdb.get_key_value_list()
            for key, value in key_value_events:
                value_dict = json.loads(value.decode("utf-8"))
                if value_dict["resp_id"] == input_data["resp_id"]:
                    self.tdb.pop(key)
        except Exception as ex:
            raise ex

        return "ok"
