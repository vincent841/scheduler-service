import strawberry
from gql.gql_types import ScheduleEventInput, RegisteredEvent
from gql.gql_utils import convert_schevent_to_dict

from schedule.schedule_event_handler import ScheduleEventHandler


"""
****************************************************************************************************************
Mutation
****************************************************************************************************************
"""


@strawberry.type
class Mutation:
    @strawberry.mutation
    def register_schedule(self, registration: ScheduleEventInput) -> RegisteredEvent:
        req_schedule = convert_schevent_to_dict(registration)
        schedule_register = ScheduleEventHandler()
        result = schedule_register.register(req_schedule)

        # return RegisteredEvent(name=result["name"], resp_id=result["resp_id"])
        return RegisteredEvent.from_dict(result)

    @strawberry.mutation
    def unregister_schedule(self, schedule_name: str) -> RegisteredEvent:
        schedule_register = ScheduleEventHandler()
        result = schedule_register.unregister(schedule_name)
        return RegisteredEvent.from_dict(result)
