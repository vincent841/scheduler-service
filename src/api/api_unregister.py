import traceback

from schedule.schedule_event_handler import ScheduleEventHandler

import sys
from helper.logger import Logger

log_info = Logger.get("apiunr", Logger.Level.INFO, sys.stdout).info
log_error = Logger.get("apiunr", Logger.Level.ERROR, sys.stderr).error


def api_unregister(unregister_data):
    log_info(f"request unregistration: {unregister_data}")
    try:
        schedule_register = ScheduleEventHandler()
        return schedule_register.unregister(unregister_data)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error": f'{unregister_data["name"]}: {ex}'}
