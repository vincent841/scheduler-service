import os
import json
import asyncio
import uuid

from config import Config
from localqueue.timestamp_queue import TimestampQueue
from schedule.schedule_next import ScheduleEventNext
from task.task_mgr import TaskManager
from task.task_import import TASK_ACTIVE_MODULE_LIST
from helper.util import convert_bytearray_to_dict

import sys
from helper.logger import Logger

log_debug = Logger.get("schevt", Logger.Level.DEBUG, sys.stdout).debug
log_info = Logger.get("schevt", Logger.Level.INFO, sys.stdout).info
log_warning = Logger.get("schevt", Logger.Level.WARNING, sys.stdout).warning
log_error = Logger.get("schevt", Logger.Level.ERROR, sys.stderr).error


class ScheduleEventHandler:
    TASK_RETRY_MAX = 3
    LOCAL_POD_NAME = "local-scheduler"

    # singleton constructor set
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # to be called once
        cls = type(self)
        if not hasattr(cls, "_init"):
            try:
                self.tdb = TimestampQueue(Config.evt_queue())
                self.running_schedules = dict()
                self.instance_name = ScheduleEventHandler.LOCAL_POD_NAME
                cls._init = True
            except Exception as ex:
                raise ex

    #  common constructor
    # def __init__(self):
    #     try:
    #         self.tdb = TimestampQueue(Config.evt_queue())
    #         self.running_schedules = list()
    #     except Exception as ex:
    #         raise ex

    def initialize(self):
        try:
            # get the current instance name
            self.instance_name = os.environ.get(
                "POD_NAME", ScheduleEventHandler.LOCAL_POD_NAME
            )
            if self.instance_name == ScheduleEventHandler.LOCAL_POD_NAME:
                log_warning(
                    "cannot find environment variable POD_NAME, so assume that th only one instance is running."
                )

            key_value_events = self.tdb.get_key_value_list()
            for key, value in key_value_events:
                key = key.decode("utf-8")
                value = convert_bytearray_to_dict(value)
                assert (type(key) is str) and (type(value) is dict)

                schedule_event = value
                if schedule_event["instance"] == self.instance_name:
                    schedule_event["name"] = key
                    log_debug(f"reigstering {schedule_event}")
                    self.register(schedule_event)

            log_debug("initialization done..")
        except Exception as ex:
            log_error(f"Initializaiton Error: {ex}")

    def register(self, input_data: dict):
        try:
            assert (
                input_data["name"]
                and input_data["type"]
                and input_data["schedule"]
                and input_data["task"]
            )

            # 1. check if name is duplicated.
            if input_data["name"] in self.running_schedules:
                raise Exception("duplicated name found")

            # 1.1. set the insance name
            input_data["instance"] = self.instance_name

            # 2. store this input_data to timastamp db with response id
            resp_id = uuid.uuid4()
            input_data["resp_id"] = str(resp_id)

            # 3. get the next timestamp and the delay based on schedule format
            (next_time, delay) = ScheduleEventNext.get_next_and_delay(input_data)

            # 4. update some additional data like next and retry
            # TODO: add some additional key-values (status, ...)
            input_data_task = input_data["task"]
            input_data_task["retry"] = 0
            input_data_task["next"] = next_time

            # 5. store the updated schedule event
            self.tdb.put(input_data["name"], input_data)

            # 6. start a schedule event task
            handle_event_future = asyncio.run_coroutine_threadsafe(
                self.handle_event(input_data["name"], input_data.copy(), delay),
                asyncio.get_event_loop(),
            )

            # 7. add the name of the current schedlue event to event_name list.
            #  to check the duplicated schedule name later
            self.running_schedules[input_data["name"]] = handle_event_future

            # 8. return the result with the response id
            return {"name": input_data["name"], "resp_id": str(resp_id)}
        except Exception as ex:
            raise ex

    def unregister(self, input_data: dict):
        try:
            assert type(input_data) is dict

            # 1. get all key-value data in the localqueue and find the specified name using for-iteration
            key_value_events = self.tdb.get_key_value_list()
            for key, _ in key_value_events:
                key_decoded = key.decode("utf-8")
                # 2. pop the event from localqueue if found
                if key_decoded == input_data["name"]:
                    self.tdb.pop(key)
                # 3. remove it from running_schedules and cancel it
                future_event = self.running_schedules.pop(input_data["name"], None)
                future_event.cancel()

        except Exception as ex:
            raise ex

        return {"name": input_data["name"]}

    def list(self):
        list_item = dict()
        try:
            # 1. gather all key-value data from the localqueue
            key_value_events = self.tdb.get_key_value_list()
            for key, value in key_value_events:
                value_dict = json.loads(value.decode("utf-8"))
                list_item[key.decode("utf-8")] = value_dict
        except Exception as ex:
            raise ex

        return list_item

    def register_next(self, schedule_event):
        try:
            # 1. check scheluer event type
            if schedule_event["type"] == "cron" or schedule_event["type"] == "delay":
                # 2. calculate the next timestamp and delay based on schedule_event
                (next_time, delay) = ScheduleEventNext.get_next_and_delay(
                    schedule_event
                )

                input_data_task = schedule_event["task"]

                # 3. reset the retry count
                input_data_task["retry"] = 0
                # 4. set next timestamp
                input_data_task["next"] = next_time

                # 5. set the evetn to the localqueue
                self.tdb.put(schedule_event["name"], schedule_event)

                handle_event_future = asyncio.run_coroutine_threadsafe(
                    self.handle_event(
                        schedule_event["name"], schedule_event.copy(), delay
                    ),
                    asyncio.get_event_loop(),
                )
                self.running_schedules[schedule_event["name"]] = handle_event_future
        except Exception as ex:
            raise ex

    async def handle_event(self, key, value, delay):
        log_debug(f'handle_event start: {value["name"]}')
        await asyncio.sleep(delay)

        try:
            task_info = value["task"]
            task_cls = TaskManager.get(task_info["type"])
            task = task_cls()
            task.connect(**task_info)
            res = await task.run(**value)
            log_debug(f'handle_event done: {value["name"]}, res: {str(res)}')

            if res:
                # put the next schedule
                self.register_next(value)
            else:
                # increase the retry count
                task_info["retry"] += 1
                self.tdb.put(key, value)
                # this event will be sent to DLQ if retry count limit is reached to the limit
                if task_info["retry"] >= ScheduleEventHandler.TASK_RETRY_MAX:
                    self.tdb.put_to_dlq(key, value)
                    self.tdb.pop(key)

        except Exception as ex:
            log_error(f"Exception: {ex}")

            # increase the retry count
            task_info["retry"] += 1
            self.tdb.put(key, value)
            # this event will be sent to DLQ if retry count limit is reached to the limit
            if task_info["retry"] >= ScheduleEventHandler.TASK_RETRY_MAX:
                self.tdb.put_to_dlq(key, value)
                self.tdb.pop(key)
