import traceback

from schedule.schedule_event_handler import ScheduleEventHandler

import sys
from helper.logger import Logger

log_message = Logger.get("aplist", Logger.Level.INFO, sys.stdout)

log_debug = log_message.debug
log_info = log_message.info
log_warning = log_message.warning
log_error = log_message.error


def api_list(input_params):
    log_info(f"request list data (input_params = {input_params})")
    try:
        schedule_handler = ScheduleEventHandler()
        return schedule_handler.list(input_params)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error(list)": f": {ex}"}
