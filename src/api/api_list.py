import json
import traceback

from schedule.schedule_event_handler import ScheduleEventHandler

import sys
from helper.logger import Logger

log_info = Logger.get("aplist", Logger.Level.INFO, sys.stdout).info
log_error = Logger.get("aplist", Logger.Level.ERROR, sys.stderr).error


def api_list():
    log_info("request list data")
    try:
        schedule_handler = ScheduleEventHandler()
        return schedule_handler.list()
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error(list)": f": {ex}"}
