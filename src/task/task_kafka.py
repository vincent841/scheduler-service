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

    async def run(self, **kargs) -> bool:
        try:
            task_info = kargs["task"]
            connection = task_info["connection"]
            topic = connection["topic"]
            produce_data = (
                json.dumps(task_info["data"])
                if type(task_info["data"]) is dict
                else str(task_info["data"])
            ).encode()

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

        return True


TaskManager.register("kafka", TaskKafka)
