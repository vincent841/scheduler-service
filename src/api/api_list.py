import json
import traceback

from schedule.schedule_event_handler import ScheduleEventHandler


def api_list():
    print("request list data")
    try:
        schedule_handler = ScheduleEventHandler()
        return schedule_handler.list()
    except Exception as ex:
        print(traceback.format_exc())
        return {"error(list)": f": {ex}"}
