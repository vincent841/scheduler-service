import asyncio
import aioredis

from task.task_mgr import TaskManager
from task.task_abstract import Task

import sys
from helper.logger import Logger

log_message = Logger.get("tkreds", Logger.Level.INFO, sys.stdout)
log_debug = log_message.debug
log_info = log_message.info
log_warning = log_message.warning
log_error = log_message.error


class TaskRedis(Task):
    def get_name(self):
        return "redis"

    def connect(self, **kargs):
        pass

    async def run(self, **kargs) -> bool:
        try:
            task_info = kargs["task"]
            connection = task_info["connection"]
            topic = task_info["topic"]
            data = task_info["data"]

            log_debug(f"connection: {connection}")
            redis_cli = aioredis.from_url(connection["host"])

            log_debug(f"topic: {topic}, data: {data}")
            await redis_cli.publish(topic, data)

        except Exception as ex:
            log_error("Exception: ", ex)


TaskManager.register("redis", TaskRedis)
