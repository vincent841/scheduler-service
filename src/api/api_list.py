import json
import traceback

from schedule.schedule_event_handler import ScheduleEventHandler

import sys
from helper.logger import Logger

log_info = Logger.get("aplist", Logger.Level.INFO, sys.stdout).info
log_error = Logger.get("aplist", Logger.Level.ERROR, sys.stderr).error


def api_list(input_params):
    log_info(f"request list data (input_params = {input_params})")
    try:
        schedule_handler = ScheduleEventHandler()
        return schedule_handler.list(input_params)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error(list)": f": {ex}"}
