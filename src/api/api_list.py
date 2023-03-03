import json
import traceback

from schedule.schedule_event_handler import ScheduleEventHandler


def api_list():
    print(f"request list data")
    try:
        schedule_register = ScheduleEventHandler()
        resp = schedule_register.list()
        resp = json.dupms(resp)
        return {
            "list": resp,
        }
    except Exception as ex:
        print(traceback.format_exc())
        return {"error(list)": f": {ex}"}
