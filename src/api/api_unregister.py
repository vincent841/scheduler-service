import traceback

from schedule.schedule_event_handler import ScheduleEventHandler


def api_unregister(unregister_data):
    print(f"request unregistration: {unregister_data}")
    try:
        schedule_register = ScheduleEventHandler()
        return schedule_register.unregister(unregister_data)
    except Exception as ex:
        print(traceback.format_exc())
        return {"error": f'{unregister_data["name"]}: {ex}'}
