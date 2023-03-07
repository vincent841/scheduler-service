import traceback

from schedule.schedule_event_handler import ScheduleEventHandler


def api_register(req_schedule):
    print(f"request register data: {req_schedule}")
    try:
        schedule_register = ScheduleEventHandler()
        return schedule_register.register(req_schedule)
    except Exception as ex:
        print(traceback.format_exc())
        return {"error": f'{req_schedule["name"]}: {ex}'}
