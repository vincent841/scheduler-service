import json
from confluent_kafka import Producer

from eventbus.eventbus_mgr import EventBusManager
from eventbus.eventbus_abstract import EventBus


class EventBusRedis(EventBus):
    def get_name(self):
        return "redis"

    def connect(self, **kargs):
        pass

    def trigger(self, **kargs):
        pass


EventBusManager.register("redis", EventBusRedis)
