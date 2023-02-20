from pydantic import BaseModel
from db.timestamp_db import TimestampDB

from config import SCHEDULE_DBNAME


class ScheduleEvent(BaseModel):
    name: str
    type: str
    priority: str
    schedule: str
    data: int


class ScheduleEventRegister:
    def __init__(self, event: ScheduleEvent):
        self.event = event
        try:
            self.tdb = TimestampDB(SCHEDULE_DBNAME)
            assert (
                self.event["name"]
                and self.event["type"]
                and self.event["data"]
                and self.event["tstamp"]
            )
        except Exception as ex:
            raise ex

    def register(self):
        try:
            # arrange schedule_data as input event without tstamp
            tdb_data = self.event.copy()
            del tdb_data["tstamp"]
            self.tdb.put(self.event["tstamp"], tdb_data)
        except Exception as ex:
            raise ex
