import json
from confluent_kafka import Producer

from task.task_mgr import TaskManager
from task.task_abstract import Task

"""
TODO: change the kafka module to 'aiokakfa'
"""


class TaskKafka(Task):
    def __init__(self):
        self.producer = None

    def get_name(self):
        return "kafka"

    def connect(self, **kargs):
        try:
            self.producer = Producer({"bootstrap.servers": kargs["host"]})
            self.producer.poll(0)
        except Exception as ex:
            pass

    async def run(self, **kargs):
        try:
            produce_data = (
                json.dumps(kargs["data"])
                if type(kargs["data"]) is dict
                else str(kargs["data"])
            ).encode("utf-8")

            # Asynchronously produce a message, the delivery report callback
            # will be triggered from poll() above, or flush() below, when the message has
            # been successfully delivered or failed permanently.
            if kargs["service"]:
                self.producer.produce(kargs["service_topic"], produce_data)
            else:
                self.producer.produce(kargs["resp_topic"], produce_data)

            self.producer.poll(0)
        except Exception as ex:
            print("Exception: ", ex)
        finally:
            # Wait for any outstanding messages to be delivered and delivery report
            # callbacks to be triggered.
            self.producer.flush()


TaskManager.register("kafka", TaskKafka)
