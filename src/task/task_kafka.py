import json
from aiokafka import AIOKafkaProducer

from task.task_mgr import TaskManager
from task.task_abstract import Task

"""
TODO: change the kafka module to 'aiokakfa'
"""


class TaskKafka(Task):
    def __init__(self):
        pass

    def get_name(self):
        return "kafka"

    def connect(self, **kargs):
        pass

    async def run(self, **kargs):
        try:
            produce_data = (
                json.dumps(kargs["data"])
                if type(kargs["data"]) is dict
                else str(kargs["data"])
            ).encode("utf-8")

            connection = kargs["connection"]

            topic = connection["topic"]

            producer = AIOKafkaProducer(bootstrap_servers=connection["host"])
            # Get cluster layout and initial topic/partition leadership information
            await producer.start()
            try:
                # Produce message
                await producer.send_and_wait(topic, produce_data)
            finally:
                # Wait for all pending messages to be delivered or expire.
                await producer.stop()

        except Exception as ex:
            print("Exception: ", ex)
        finally:
            # Wait for any outstanding messages to be delivered and delivery report
            # callbacks to be triggered.
            await producer.stop()


TaskManager.register("kafka", TaskKafka)
