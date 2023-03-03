import traceback

from schedule.schedule_event_handler import ScheduleEventHandler


def api_unregister(unregister_data):
    print(f"unregister: {unregister_data}")
    try:
        schedule_register = ScheduleEventHandler()
        resp = schedule_register.unregister(unregister_data)
        return {"resp_id": unregister_data["resp_id"]}
    except Exception as ex:
        print(traceback.format_exc())
        return {"error": f'{unregister_data["name"]}: {ex}'}
