import traceback

from schedule.schedule_event_handler import ScheduleEventHandler

import sys
from helper.logger import Logger


log_message = Logger.get("apimtd", Logger.Level.INFO, sys.stdout)

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
        return {"error": f'{req_schedule["client"]}: {ex}'}


def api_unregister(unregister_data):
    log_info(f"request unregistration: {unregister_data}")
    try:
        schedule_register = ScheduleEventHandler()
        resp_id = unregister_data.get("resp_id", "")
        return schedule_register.unregister(resp_id)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error": f'{unregister_data["resp_id"]}: {ex}'}


def api_list(input_params):
    log_info(f"request list data (input_params = {input_params})")
    try:
        schedule_handler = ScheduleEventHandler()
        return schedule_handler.list(input_params)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error(list)": f": {ex}"}
