from pydantic import BaseModel
from db.timestamp_db import TimestampDB

from config import Config
import uuid
from croniter import croniter
from datetime import datetime

from schedule.schedule_next import ScheduleEventNext


class ScheduleEvent(BaseModel):
    name: str
    type: str
    schedule: str
    data: str


class ScheduleEventRegister:
    def __init__(self, event: ScheduleEvent):
        self.event = event
        try:
            self.tdb = TimestampDB(Config.evt_queue())
            assert (
                self.event["name"]
                and self.event["type"]
                and self.event["schedule"]
                and self.event["data"]
            )
        except Exception as ex:
            raise ex

    def register(self) -> str:
        try:
            # generate response id
            resp_id = uuid.uuid4()

            # store this event to timastamp db
            self.event["resp"] = str(resp_id)

            next_time = ScheduleEventNext.process_next(self.event)

            self.tdb.put(next_time, self.event)
            return str(resp_id)
        except Exception as ex:
            raise ex
