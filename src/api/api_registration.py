import traceback

from api.api_type import ENSRegistrationData, ENSRegistrationResult


def process_registration(req_schedule) -> ENSRegistrationResult:
    print(f"Registration Input Data: {req_schedule}")
    try:
        schedule_registration = ENSRegistrationData(req_schedule)
        schedule_registration_result = schedule_registration.run()
        return {"type": req_schedule["type"], "result": schedule_registration_result}
    except Exception as ex:
        print(traceback.format_exc())
        return {"error": f'{req_schedule["type"]}: {str(type(ex))} - {ex}'}
