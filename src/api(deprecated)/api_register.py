import traceback

from schedule.schedule_event_handler import ScheduleEventHandler

import sys
from helper.logger import Logger


log_message = Logger.get("apireg", Logger.Level.INFO, sys.stdout)

log_debug = log_message.debug
log_info = log_message.info
log_warning = log_message.warning
log_error = log_message.error


def api_register(req_schedule):
    log_info(f"request register data: {req_schedule}")
    try:
        schedule_register = ScheduleEventHandler()
        return schedule_register.register(req_schedule)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error": f'{req_schedule["name"]}: {ex}'}
