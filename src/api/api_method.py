import traceback

from schedule.schedule_event_handler import ScheduleEventHandler

import sys
from helper.logger import Logger


log_message = Logger.get("apimtd", Logger.Level.INFO, sys.stdout)

log_debug = log_message.debug
log_info = log_message.info
log_warning = log_message.warning
log_error = log_message.error


def api_register(input_req):
    log_info(f"request registration: {input_req}")
    try:
        schedule_register = ScheduleEventHandler()
        return schedule_register.register(input_req)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error": f'{input_req["client"]}: {ex}'}


def api_unregister(input_req):
    log_info(f"request unregistration: {input_req}")
    try:
        schedule_register = ScheduleEventHandler()
        resp_id = input_req.get("resp_id", "")
        return schedule_register.unregister(resp_id)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error": f'{input_req["resp_id"]}: {ex}'}


def api_update(input_req):
    log_info(f"request update: {input_req}")
    try:
        schedule_register = ScheduleEventHandler()
        return schedule_register.update(input_req)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error": f'{input_req["resp_id"]}: {ex}'}


def api_list(input_req):
    log_info(f"request list: {input_req}")
    try:
        schedule_handler = ScheduleEventHandler()
        return schedule_handler.list(input_req)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error(list)": f": {ex}"}


def api_reset():
    log_info(f"request reset")
    try:
        schedule_handler = ScheduleEventHandler()
        return schedule_handler.reset()
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error(list)": f": {ex}"}
