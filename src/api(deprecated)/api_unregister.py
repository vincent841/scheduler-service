import traceback

from schedule.schedule_event_handler import ScheduleEventHandler

import sys
from helper.logger import Logger

log_message = Logger.get("apiunr", Logger.Level.INFO, sys.stdout)

log_debug = log_message.debug
log_info = log_message.info
log_warning = log_message.warning
log_error = log_message.error


def api_unregister(unregister_data):
    log_info(f"request unregistration: {unregister_data}")
    try:
        schedule_register = ScheduleEventHandler()
        return schedule_register.unregister(unregister_data)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error": f'{unregister_data["name"]}: {ex}'}
