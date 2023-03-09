import sys
import httpx

from task.task_mgr import TaskManager
from task.task_abstract import Task

from helper.logger import Logger

log_info = Logger.get("tkrest", Logger.Level.INFO, sys.stdout).info
log_debug = Logger.get("tkrest", Logger.Level.DEBUG, sys.stdout).debug
log_error = Logger.get("tkrest", Logger.Level.ERROR, sys.stderr).error


class TaskRest(Task):
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.host = ""
        self.headers = dict()
        self.data = dict()

    def get_name(self):
        return "rest"

    def connect(self, **kargs):
        try:
            connection_info = kargs["connection"]
            self.host = connection_info["host"]
            self.headers = connection_info.get("headers", {})
            self.data = connection_info.get("data", {})
        except Exception as ex:
            log_error(f"Exception: {ex}")
            raise ex

    async def run(self, **kargs):
        result = False
        try:
            # like {"Accept": "application/json", "Content-Type": "application/json"}
            headers = self.headers or {}
            data = self.data or {}
            res = await self.client.post(
                self.host, headers=headers, data=data, timeout=600
            )
            log_debug(f"result: {res.status_code}")
            result = True if res.status_code == 200 else False

        except Exception as ex:
            log_error("Exception: ", ex)

        return result


TaskManager.register("rest", TaskRest)
