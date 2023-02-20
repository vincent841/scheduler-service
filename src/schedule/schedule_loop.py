import threading
import time
from dataclasses import dataclass, field

from db.timestamp_db import TimestampDB


@dataclass
class EventItem:
    tstamp: int
    name: str
    type: str
    data: dict


class TimestampEventLoop(threading.Thread):
    RESOLUTION = 0.1  # 100ms

    def __init__(self, db_path):
        threading.Thread.__init__(self)
        self.tdb = TimestampDB(db_path)
        self.event_list = list()
        self.loop_delay = 10

    def close(self):
        self.tdb.close()

    def run(self, *args, **kwargs):
        while True:
            events = self.tdb.trigger_events()
            if events:
                for event in events:
                    print(event)
            time.sleep(TimestampEventLoop.RESOLUTION)
