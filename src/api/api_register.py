import traceback

from schedule.schedule_register import ScheduleEventRegister


def api_register(req_schedule):
    print(f"request register data: {req_schedule}")
    try:
        schedule_register = ScheduleEventRegister(req_schedule)
        schedule_register.register()
        return {"type": req_schedule["name"], "status": "registered"}
    except Exception as ex:
        print(traceback.format_exc())
        return {"error": f'{req_schedule["type"]}: {str(type(ex))} - {ex}'}
