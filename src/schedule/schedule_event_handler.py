import json
import asyncio
import uuid
from pydantic import BaseModel

from config import Config
from localqueue.timestamp_queue import TimestampQueue
from schedule.schedule_next import ScheduleEventNext
from task.task_mgr import TaskManager
from task.task_import import TASK_ACTIVE_MODULE_LIST


class ScheduleTask(BaseModel):
    type: str
    connection: str
    data: dict


class ScheduleRegisterData(BaseModel):
    name: str
    type: str
    schedule: str
    task: ScheduleTask


class ScheduleUnregisterData(BaseModel):
    resp_id: str


class ScheduleEventHandler:
    def __init__(self):
        try:
            self.tdb = TimestampQueue(Config.evt_queue())
            self.event_name_list = list()
        except Exception as ex:
            raise ex

    def register(self, input_data: dict) -> str:
        try:
            assert (
                input_data["name"]
                and input_data["type"]
                and input_data["schedule"]
                and input_data["task"]
            )

            # check if name is duplicated.
            if input_data["name"] in self.event_name_list:
                raise Exception("duplicated name found")

            # store this input_data to timastamp db with response id
            resp_id = uuid.uuid4()
            input_data["resp_id"] = str(resp_id)

            (next_time, delay) = ScheduleEventNext.get_next_and_delay(input_data)

            # TODO: add some additional key-values (status, ...)
            self.tdb.put(next_time, input_data)
            self.event_name_list.append(input_data["name"])

            event_data = input_data.copy()
            asyncio.run_coroutine_threadsafe(
                ScheduleEventHandler.handle_event(event_data, delay),
                asyncio.get_event_loop(),
            )

            return {"name": input_data["name"], "resp_id": str(resp_id)}
        except Exception as ex:
            raise ex

    def unregister(self, input_data: dict):
        try:
            key_value_events = self.tdb.get_key_value_list()
            for key, value in key_value_events:
                value_dict = json.loads(value.decode("utf-8"))
                if value_dict["resp_id"] == input_data["resp_id"]:
                    self.tdb.pop(key)
            self.event_name_list.remove(input_data["name"])
        except Exception as ex:
            raise ex

        return "ok"

    def list(self):
        item_list = list()
        try:
            key_value_events = self.tdb.get_key_value_list()
            for key, value in key_value_events:
                value_dict = json.loads(value.decode("utf-8"))
                item_list.append({key.decode("utf-8"), value_dict})
        except Exception as ex:
            raise ex

        return item_list

    @staticmethod
    async def handle_event(event, delay):
        print(f'handle_event start: {event["name"]}')
        await asyncio.sleep(delay)

        try:
            task_info = event["task"]
            task_cls = TaskManager.get(task_info["type"])
            task = task_cls()
            task.connect(**task_info)
            res = await task.run(**event)
            print(f'handle_event done: {event["name"]}, res: {str(res)}')
        except Exception as ex:
            print(f"Exception: {ex}")
