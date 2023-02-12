from pydantic import BaseModel
from event_scheduler import EventScheduler
from event_trigger import ENSEventTrigger


class ENSEvent(BaseModel):
    name: str
    type: str
    schedule: str
    data: dict


class ENSEventManager:
    def __init__(self, config=None):
        self.event_sched = EventScheduler("ens_event_scheduler")

        # TODO: create an object tracker by configuration
        self.event_trigger = ENSEventTrigger(config)

        # prepare event registrations
        self.events: ENSEvent = list()

    def start(self) -> None:
        self.event_sched.start()

    def stop(self, hard_stop: bool = False) -> None:
        self.event_sched.stop(hard_stop)

    def register_delay(self, name, delay, recurring=False):
        # if recurring == False:
        #     self.event_sched.enter(5, 0, self.event_trigger, ('5 seconds has passed since this event was entered!',))
        # if recurring = True:
        #     event_scheduler.enter_recurring(10, 0, self.event_trigger, ('10 second interval has passed!',))
        pass

    def register_timestamp(self, name, timestamp):
        pass

    def register_cron(self, name, cron):
        pass
