from pydantic import BaseModel
from event_scheduler import EventScheduler

from helper.config import AppConfig
from event.event_trigger import ENSEventTrigger


class ENSEvent(BaseModel):
    name: str
    type: str
    priority: str
    schedule: str
    data: dict


class ENSEventManager:
    _instance = None
    CONFIGURATION_FILE_PATH = "config/config.yaml"

    def __init__(self):
        raise RuntimeError("Call instance() instead")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            # initilaize class members
            cls.initialize(cls)
        return cls._instance

    def initialize(self):
        self.event_sched = EventScheduler("ens_event_scheduler")

        # TODO: create an object tracker by configuration
        self.event_trigger = ENSEventTrigger()

        # prepare event registrations
        self.events: ENSEvent = list()

        # initialize the configuraiton
        self.config = AppConfig(
            config_yaml_file=ENSEventManager.CONFIGURATION_FILE_PATH
        )

    def start(self) -> None:
        self.event_sched.start()

    def stop(self, hard_stop: bool = False) -> None:
        self.event_sched.stop(hard_stop)

    @classmethod
    def trigger_event(cls, name, data):
        print(f"triggered this event: [{name}]-[{data}]")

    def register(self, type, schedule, name, data):
        if type == "abs":
            self.register_timestamp(schedule, name, data)
        elif type == "cron":
            self.register_cron(schedule, name, data)
        elif type == "delay":
            self.register_delay(schedule, name, data, recurring=False)
        elif type == "delay_recur":
            self.register_delay(schedule, name, data, recurring=True)
        else:
            raise Exception(f"Undefined event type here... {type}")

    def register_delay(self, name, delay, data, recurring=False):
        # if recurring == False:
        #     self.event_sched.enter(5, 0, self.event_trigger, ('5 seconds has passed since this event was entered!',))
        # if recurring = True:
        #     event_scheduler.enter_recurring(10, 0, self.event_trigger, ('10 second interval has passed!',))
        pass

    def register_timestamp(self, schedule, priority, name, data):
        # fire the evebnt right now
        if schedule == 0:
            ENSEventTrigger.trigger_event(name, data)
        else:
            self.event_sched.enterabs(
                schedule,
                priority,
                ENSEventManager.trigger_event,
                arguments=(name, data),
            )

    def register_cron(self, schedule, name, data):
        pass


g_eventmgr = ENSEventManager.instance()
