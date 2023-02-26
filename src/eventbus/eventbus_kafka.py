import json
from confluent_kafka import Producer

from eventbus.eventbus_mgr import EventBusManager
from eventbus.eventbus_abstract import EventBus


class EventBusKafka(EventBus):
    def __init__(self):
        self.producer = None
        self.topic = ""

    def get_name(self):
        return "kafka"

    def connect(self, **kargs):
        try:
            self.producer = Producer({"bootstrap.servers": kargs["host"]})
            self.topic = kargs["topic"]
            self.producer.poll(0)

        except Exception as ex:
            pass

    def trigger(self, **kargs):
        try:
            produce_data = (
                json.dumps(kargs["data"])
                if type(kargs["data"]) is dict
                else str(kargs["data"])
            )

            # Asynchronously produce a message, the delivery report callback
            # will be triggered from poll() above, or flush() below, when the message has
            # been successfully delivered or failed permanently.
            self.producer.produce(
                self.topic,
                produce_data.encode("utf-8"),
            )

            self.producer.poll(0)
        except Exception as ex:
            print("Exception: ", ex)

        finally:
            # Wait for any outstanding messages to be delivered and delivery report
            # callbacks to be triggered.
            self.producer.flush()


EventBusManager.register("kafka", EventBusKafka)
