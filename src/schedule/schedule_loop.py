import sys
import threading
import time
from dataclasses import dataclass

from db.timestamp_db import TimestampDB
from schedule.schedule_next import ScheduleEventNext
from config import Config
from eventbus.eventbus_mgr import EventBusManager

import eventbus.eventbus_import as im


from helper.logger import Logger

log_debug = Logger.get("schloop", Logger.Level.DEBUG, sys.stdout).debug
log_error = Logger.get("schloop", Logger.Level.ERROR, sys.stderr).error


@dataclass
class EventItem:
    tstamp: int
    name: str
    type: str
    data: dict


class ScheduleEventLoop(threading.Thread):
    RESOLUTION = 0.1  # 100ms
    EVENTBUS_ACTIVE_LIST = im.EVENTBUS_ACTIVE_MODULE_LIST

    def __init__(self, db_path):
        threading.Thread.__init__(self)
        self.tdb = TimestampDB(db_path)
        self.event_list = list()
        self.event_bus = None

    def close(self):
        self.tdb.close()

    def configure(self):
        # TODO: prepare the eventbus & services based on configuration
        try:
            evtbus = Config.eventbus()
            evtbus_cls = EventBusManager.get(evtbus["type"])
            self.event_bus = evtbus_cls()
            self.event_bus.connect(**evtbus)
        except Exception as ex:
            print("configrue error: \n", ex)

        print("configuration is done.")

    def process_next(self, event):
        next_time = ScheduleEventNext.process_next(event)
        self.tdb.put(next_time, event)

    def run(self, *args, **kwargs):
        self.configure()
        while True:
            events = self.tdb.trigger_events()
            if events:
                for event in events:
                    # TODO: process backend
                    log_debug(event)
                    self.event_bus.trigger(**event)

                    # put the next event to tdb
                    # TODO: check if the currebt event is done well or put it to the dlq event
                    self.process_next(event)

            # delay the time
            time.sleep(ScheduleEventLoop.RESOLUTION)
