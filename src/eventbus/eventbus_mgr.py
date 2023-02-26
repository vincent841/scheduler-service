from eventbus.eventbus_abstract import EventBus


class EventBusManager:
    EVENTBUS_DATA = dict()

    @staticmethod
    def register(type: str, backend_cls: EventBus):
        EventBusManager.EVENTBUS_DATA[type] = backend_cls

    @staticmethod
    def get(type: str):
        evtbus_type = None
        try:
            evtbus_type = EventBusManager.EVENTBUS_DATA[type]
        except KeyError as keyerr:
            print("not support this type")

        return evtbus_type

    @staticmethod
    def all():
        return EventBusManager.EVENTBUS_DATA
