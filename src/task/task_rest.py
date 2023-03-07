import sys
import httpx

from task.task_mgr import TaskManager
from task.task_abstract import Task

from helper.logger import Logger

log_debug = Logger.get("task_rest", Logger.Level.DEBUG, sys.stdout).debug
log_error = Logger.get("task_rest", Logger.Level.ERROR, sys.stderr).error


class TaskRest(Task):
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.host = ""
        self.headers = dict()

    def get_name(self):
        return "rest"

    def connect(self, **kargs):
        try:
            connection_info = kargs["connection"]
            self.host = connection_info["host"]
            self.headers = connection_info["headers"]
        except Exception as ex:
            print(f"Exception: {ex}")
            raise ex

    async def run(self, **kargs):
        try:
            # like {"Accept": "application/json", "Content-Type": "application/json"}
            headers = self.headers or {}
            res = await self.client.post(self.host, headers=headers)
            log_debug(f"{self.host}")

        except Exception as ex:
            print("Exception: ", ex)
            res = None
            raise ex
        finally:
            pass

        return res


TaskManager.register("rest", TaskRest)
