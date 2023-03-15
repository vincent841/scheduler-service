import os
import asyncio
import uuid
from datetime import datetime

from config import Config
from localqueue.local_queue import LocalQueue
from schedule.schedule_event_type import ScheduleEventType
from schedule.scheduler_event import ScheduleTaskStatus
from task.task_mgr import TaskManager
from task.task_import import TASK_ACTIVE_MODULE_LIST

from db.db_engine import initialize_global_database, get_session
from db.tables.table_schedule_history import ScheduleEventHistory


import sys
from helper.logger import Logger


log_message = Logger.get("schevt", Logger.Level.INFO, sys.stdout)

log_debug = log_message.debug
log_info = log_message.info
log_warning = log_message.warning
log_error = log_message.error


class ScheduleEventHandler:
    TASK_RETRY_MAX = 3
    DEFAULT_LOCAL_POD_NAME = "local-scheduler"

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
                self.tdb = LocalQueue(Config.evt_queue())
                self.running_schedules = dict()
                self.instance_name = ScheduleEventHandler.DEFAULT_LOCAL_POD_NAME
                cls._init = True
            except Exception as ex:
                raise ex

    #  common constructor
    # def __init__(self):
    #     try:
    #         self.tdb = LocalQueue(Config.evt_queue())
    #         self.running_schedules = list()
    #     except Exception as ex:
    #         raise ex

    def initialize(self):
        try:
            # get the current instance name
            self.instance_name = os.environ.get(
                "POD_NAME", ScheduleEventHandler.DEFAULT_LOCAL_POD_NAME
            )
            if self.instance_name == ScheduleEventHandler.DEFAULT_LOCAL_POD_NAME:
                log_warning(
                    "cannot find environment variable POD_NAME, so assume that th only one instance is running."
                )

            #
            key_value_events = self.tdb.get_key_value_list()
            for key, value in key_value_events:
                assert (type(key) is str) and (type(value) is dict)

                schedule_event = value
                if schedule_event["instance"] == self.instance_name:
                    schedule_event["name"] = key
                    log_info(f"reigstering {schedule_event}")
                    self.register(schedule_event)

            log_info("initialization done..")
        except Exception as ex:
            log_error(f"Initializaiton Error: {ex}")

    def register(self, schedule_event: dict):
        try:
            assert (
                schedule_event["name"]
                and schedule_event["type"]
                and schedule_event["task"]
            )

            # 1. check if name is duplicated.
            if schedule_event["name"] in self.running_schedules:
                raise Exception("duplicated name found")

            # 1.1. set the insance name
            schedule_event["instance"] = self.instance_name

            # 2. store this schedule_event to timastamp db with response id
            resp_id = uuid.uuid4()
            schedule_event["resp_id"] = str(resp_id)

            # 3. get the next timestamp and the delay based on schedule format
            (next_time, delay) = ScheduleEventType.get_next_and_delay(schedule_event)

            # TODO: add some additional key-values (status, ...)
            input_data_task = schedule_event["task"]
            # 4.1 check if task type is available
            if not input_data_task["type"] in TaskManager.all():
                raise Exception("task type unavailable.")
            # 4.2 update some additional data like next and retry
            input_data_task["retry_count"] = 0
            input_data_task["next"] = next_time
            input_data_task["status"] = ScheduleTaskStatus.IDLE
            input_data_task["iteration"] = 0
            input_data_task["lastRun"] = None

            # 5. store the updated schedule event
            self.tdb.put(schedule_event["name"], schedule_event)
            self.save_schevt_to_db("register", schedule_event)

            # 6. start a schedule event task
            handle_event_future = asyncio.run_coroutine_threadsafe(
                self.handle_event(schedule_event["name"], schedule_event.copy(), delay),
                asyncio.get_event_loop(),
            )

            # 7. add the name of the current schedlue event to event_name list.
            #  to check the duplicated schedule name later
            self.running_schedules[schedule_event["name"]] = handle_event_future

            # 8. return the result with the response id
            return {"name": schedule_event["name"], "resp_id": str(resp_id)}
        except Exception as ex:
            raise ex

    def unregister(self, schedule_event: dict):
        try:
            assert type(schedule_event) is dict

            # 1. get all key-value data in the localqueue and find the specified name using for-iteration
            key_value_events = self.tdb.get_key_value_list()
            log_debug(f"*** get_key_value_list: {key_value_events}")
            for key, registered_event in key_value_events:
                # 2. pop the event from localqueue if found
                if key == schedule_event["name"]:
                    self.tdb.pop(key)
                    self.save_schevt_to_db("unregister", registered_event)
                    # 3. remove it from running_schedules and cancel it
                    future_event = self.running_schedules.pop(
                        schedule_event["name"], None
                    )
                    future_event.cancel()

        except Exception as ex:
            raise ex

        return registered_event

    def list(self, input_params: dict):
        list_item = dict()

        # 1. fetch the dlq flag, True or False
        dlq = input_params.get("dlq", False)

        try:
            # 2. gather all key-value data from the localqueue
            key_value_events = self.tdb.get_key_value_list(dlq)
            for key, value in key_value_events:
                list_item[key] = value
        except Exception as ex:
            raise ex

        return list_item

    def register_next(self, schedule_event):
        try:
            # 1. check if scheluer event type is
            if ScheduleEventType.is_recurring(schedule_event["type"]):
                # 2. calculate the next timestamp and delay based on schedule_event
                (next_time, delay) = ScheduleEventType.get_next_and_delay(
                    schedule_event
                )

                input_data_task = schedule_event["task"]

                # 3. reset the retry count
                input_data_task["retry_count"] = 0
                # 4. set next timestamp
                input_data_task["next"] = next_time

                # 5. set the evetn to the localqueue
                self.tdb.put(schedule_event["name"], schedule_event)
                self.save_schevt_to_db("register", schedule_event)

                handle_event_future = asyncio.run_coroutine_threadsafe(
                    self.handle_event(
                        schedule_event["name"], schedule_event.copy(), delay
                    ),
                    asyncio.get_event_loop(),
                )
                self.running_schedules[schedule_event["name"]] = handle_event_future
            else:
                # pop this schedule event if it is not ono of recurrring schedule types.
                self.tdb.pop(schedule_event["name"])
                self.running_schedules.pop(schedule_event["name"], None)
        except Exception as ex:
            raise ex

    def save_schevt_to_db(self, event, schedule_event):
        try:
            task_info = schedule_event.get("task", {})
            if task_info:
                hischeck = task_info.get("history_check", False)
                if hischeck:
                    (host, port, id, pw, db) = Config.db()
                    initialize_global_database(id, pw, host, port, db)
                    with get_session() as db_session:
                        schevt_history = ScheduleEventHistory(
                            event=event,
                            name=schedule_event.get("name"),
                            type=schedule_event.get("type"),
                            schedule=schedule_event.get("schedule"),
                            task_type=task_info.get("type"),
                            task_connection=task_info.get("connection"),
                            task_data=task_info.get("data"),
                        )

                        db_session.add(schevt_history)
                        db_session.commit()
        except Exception as ex:
            log_error(f"can't save event to db - {ex}")

    async def handle_event(self, key, schedule_event, delay):
        try:
            log_info(f'handle_event start: {schedule_event["name"]}')

            # 1. put it into the qeueue with the status 'waiting'
            task_info = schedule_event["task"]
            task_info["status"] = ScheduleTaskStatus.WAITING
            self.tdb.put(key, schedule_event)

            # 2. sleep with the input delay
            log_debug(f'*** before sleep({schedule_event["name"]})')
            await asyncio.sleep(delay)
            log_debug(f'*** after sleep({schedule_event["name"]})')

            # 3. run a task based on task parameters
            task_cls = TaskManager.get(task_info["type"])
            task = task_cls()

            task.connect(**task_info)
            res = await task.run(**schedule_event)
            log_debug(f'handle_event done: {schedule_event["name"]}, res: {str(res)}')

            # 4. handle the result of this task run
            if res:
                # 4.1 put it into the queue with status 'Done'
                task_info["status"] = ScheduleTaskStatus.DONE
                task_info["iteration"] += 1
                task_info["lastRun"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                self.tdb.put(key, schedule_event)
                self.save_schevt_to_db("done", schedule_event)

                # put the next schedule
                self.register_next(schedule_event)
            else:
                log_debug(
                    f'got the wrong response of the task({schedule_event["name"]})'
                )
                raise Exception(
                    f'got the wrong response of the task({schedule_event["name"]})'
                )

        except Exception as ex:
            log_error(f"Exception: {ex}")

            log_debug(f'failed_policy: {task_info.get("failed_policy")}')

            # 0. set the lastRun
            task_info["lastRun"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            # 1. in case that 'failed_policy' == "retry"
            if task_info.get("failed_policy", "ignore") == "retry":
                # 1.1 increase the retry count
                task_info["retry_count"] += 1
                task_info["status"] = ScheduleTaskStatus.RETRY
                task_info["lastRun"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                # 1.2 this event will be sent to DLQ if retry count limit is reached to the limit
                if task_info["retry_count"] >= task_info.get(
                    "max_retry_count", ScheduleEventHandler.TASK_RETRY_MAX
                ):
                    log_info(f'reached retry max count... {schedule_event["name"]}')

                    # 1.2.1 pop this schedule from the standard queue and put it into DLQ
                    task_info["status"] = ScheduleTaskStatus.FAILED
                    self.tdb.put(key, schedule_event, dlq=True)
                    self.tdb.pop(key)

                    # 1.2.2 update the schedule event dict and cancel it
                    future_event = self.running_schedules.pop(
                        schedule_event["name"], None
                    )
                    future_event.cancel() if future_event else None
                # 1.3 retry one more..
                else:
                    # 1.3.1 put it into the queue with the changed status
                    task_info["status"] = ScheduleTaskStatus.RETRY
                    self.tdb.put(key, schedule_event)

                    # 1.3.2 run it again and update the schedule evnet dict.
                    handle_event_future = asyncio.run_coroutine_threadsafe(
                        self.handle_event(
                            schedule_event["name"], schedule_event.copy(), delay
                        ),
                        asyncio.get_event_loop(),
                    )
                    self.running_schedules[schedule_event["name"]] = handle_event_future
            # 2. in case that 'failed_policy' == "ignore"
            else:
                # 2.1 savd the event to history db with status 'failed' and udpate the schedule event dictionary
                self.save_schevt_to_db("failed", schedule_event)
                self.tdb.pop(key)
                future_event = self.running_schedules.pop(schedule_event["name"], None)

                # 2.2 cancle the current event
                future_event.cancel() if future_event else None
