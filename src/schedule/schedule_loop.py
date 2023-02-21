import sys
import threading
import time
from dataclasses import dataclass

from db.timestamp_db import TimestampDB
from schedule.schedule_next import ScheduleEventNext


from helper.logger import Logger

log_debug = Logger.get("config", Logger.Level.DEBUG, sys.stdout).debug
log_error = Logger.get("config", Logger.Level.ERROR, sys.stderr).error


@dataclass
class EventItem:
    tstamp: int
    name: str
    type: str
    data: dict


class ScheduleEventLoop(threading.Thread):
    RESOLUTION = 0.1  # 100ms

    def __init__(self, db_path):
        threading.Thread.__init__(self)
        self.tdb = TimestampDB(db_path)
        self.event_list = list()
        self.loop_delay = 10

    def close(self):
        self.tdb.close()

    def process_next(self, event):
        next_time = ScheduleEventNext.process_next(event)
        self.tdb.put(next_time, event)

    def run(self, *args, **kwargs):
        while True:
            events = self.tdb.trigger_events()
            if events:
                for event in events:
                    # TODO: process backend
                    self.process_next(event)
                    log_debug(event)
            time.sleep(ScheduleEventLoop.RESOLUTION)
