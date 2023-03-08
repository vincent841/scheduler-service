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
        self.method = ""
        self.headers = dict()

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
        try:
            # like {"Accept": "application/json", "Content-Type": "application/json"}
            headers = self.headers or {}
            data = self.data or {}
            res = await self.client.post(
                self.host, headers=headers, data=data, timeout=600
            )
            log_info(f"result: {res}")

        except Exception as ex:
            log_error("Exception: ", ex)
            res = None
            raise ex
        finally:
            pass

        return res


TaskManager.register("rest", TaskRest)
