import json
from confluent_kafka import Producer

from task.task_mgr import TaskManager
from task.task_abstract import Task


class TaskRedis(Task):
    def get_name(self):
        return "redis"

    def connect(self, **kargs):
        pass

    async def run(self, **kargs):
        pass


TaskManager.register("redis", TaskRedis)
