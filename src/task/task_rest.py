import httpx

from task.task_mgr import TaskManager
from task.task_abstract import Task


class TaskRest(Task):
    def __init__(self):
        self.client = httpx.AsyncClient()

    def get_name(self):
        return "rest"

    def connect(self, **kargs):
        pass

    async def run(self, **kargs):
        try:
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            res = await self.client.post("https://httpbin.org/post", headers=headers)
        except Exception as ex:
            print("Exception: ", ex)
        finally:
            pass

        return res


TaskManager.register("rest", TaskRest)
