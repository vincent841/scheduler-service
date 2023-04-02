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


def api_delete_schedules(resp_id):
    log_info(f"request delete: {resp_id}")
    try:
        schedule_register = ScheduleEventHandler()
        return schedule_register.delete_schedules(resp_id)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error": f'{resp_id["resp_id"]}: {ex}'}


def api_update(input_req):
    log_info(f"request update: {input_req}")
    try:
        schedule_register = ScheduleEventHandler()
        return schedule_register.update(input_req)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error": f'{input_req["resp_id"]}: {ex}'}


def api_get_schedules(
    resp_id: str, group: str = "", application: str = "", dlq: bool = False
) -> dict:
    log_info(
        f"request get_schedules - resp_id({resp_id}), group({group}), application({application})"
    )
    try:
        schedule_handler = ScheduleEventHandler()
        return schedule_handler.get_schedules(resp_id, group, application, dlq)
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error(list)": f": {ex}"}


def api_get_groups() -> list:
    log_info(f"request api_get_groups")
    try:
        schedule_handler = ScheduleEventHandler()
        return schedule_handler.get_groups()
    except Exception as ex:
        log_error(traceback.format_exc())
        return {"error(list)": f": {ex}"}


def api_delete_schedule(group_id: str) -> dict:
    log_info(f"request delete schedule")
    try:
        schedule_handler = ScheduleEventHandler()
        return schedule_handler.delete_schedules(None, group_id)
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
