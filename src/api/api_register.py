import traceback

from schedule.schedule_event_handler import ScheduleEventHandler

import sys
from helper.logger import Logger

log_info = Logger.get("apireg", Logger.Level.INFO, sys.stdout).info
log_error = Logger.get("apireg", Logger.Level.ERROR, sys.stderr).error


def api_register(req_schedule):
    log_info(f"request register data: {req_schedule}")
    try:
        schedule_register = ScheduleEventHandler()
        return schedule_register.register(req_schedule)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error": f'{req_schedule["name"]}: {ex}'}
