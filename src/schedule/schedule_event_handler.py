import os
import asyncio
import uuid
from datetime import datetime

from config import Config
from localqueue.local_queue import LocalQueue
from schedule.schedule_event_type import ScheduleEventType, ScheduleTaskStatus
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

            key_value_events = self.tdb.get_key_value_list()
            for key, value in key_value_events:
                assert (type(key) is str) and (type(value) is dict)

                schedule_event = value
                if schedule_event["instance"] == self.instance_name:
                    log_info(f"reigstering {schedule_event}")
                    self.register(schedule_event)

            log_info("initialization done..")
        except Exception as ex:
            log_error(f"Initializaiton Error: {ex}")

    def is_connection_available(self, type: str, connection_info: dict) -> bool:
        if type == "rest":
            if not connection_info.get("host", ""):
                raise Exception(f"{type} type must have 'host'.")
        elif type == "kafka" or type == "redis":
            if not connection_info.get("topic", "") or not connection_info.get(
                "data", ""
            ):
                raise Exception(f"{type} type must have 'topic' and 'data'")
        else:
            pass

    def register(self, schedule_event: dict):
        try:
            client_info = schedule_event.get("client")
            assert (
                client_info["key"]
                and schedule_event["type"]
                and schedule_event["schedule"]
                and schedule_event["task"]
            )

            # 1. check if name is duplicated.
            if client_info["key"] in self.running_schedules:
                self.handle_duplicated_event(schedule_event)

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
            # 4.2 check if task connection is available
            input_task_connection = input_data_task["connection"]
            self.is_connection_available(input_data_task["type"], input_task_connection)
            # 4.3 update some additional data like next and retry
            input_data_task["retry_count"] = 0
            input_data_task["next"] = next_time
            input_data_task["status"] = ScheduleTaskStatus.IDLE
            input_data_task["iteration"] = 0
            input_data_task["lastRun"] = None

            # 5. store the updated schedule event
            self.tdb.put(client_info["key"], schedule_event)
            self.save_schevt_to_db("register", schedule_event)

            # 6. start a schedule event task
            handle_event_future = asyncio.run_coroutine_threadsafe(
                self.handle_event(client_info["key"], schedule_event.copy(), delay),
                asyncio.get_event_loop(),
            )

            # 7. add the name of the current schedlue event to event_name list.
            #  to check the duplicated schedule name later
            self.running_schedules[client_info["key"]] = handle_event_future

            # 8. return the result with the response id
            return {
                "name": schedule_event["name"],
                "client": {
                    "key": client_info["key"],
                    "application": client_info["application"],
                    "group": client_info["group"],
                },
                "resp_id": str(resp_id),
            }
        except Exception as ex:
            raise ex

    def handle_duplicated_event(self, schedule_event: dict):
        log_info(f"started to handle the duplicated event: {schedule_event}")
        # 0. get resp_id
        client_info = schedule_event["client"]
        input_key = client_info["key"]

        # 1. delete the previous event and cancel the current event
        self.tdb.pop(input_key)
        future_event = self.running_schedules.pop(input_key, None)
        future_event.cancel() if future_event else None

        # 2. update the record for the current schedule event
        self.save_schevt_to_db("deleted", schedule_event)

    def unregister(self, input_resp_id: str):
        try:
            if type(input_resp_id) is not str or input_resp_id == "":
                raise Exception(f"input_resp_id is not available.. {input_resp_id}")

            # 1. get all key-value data in the localqueue and find the specified name using for-iteration
            key_value_events = self.tdb.get_key_value_list()
            log_debug(f"*** get_key_value_list: {key_value_events}")

            found_count = 0
            if len(key_value_events):
                for key, registered_event in key_value_events:
                    # 2. pop the event from localqueue if found
                    resp_id = registered_event["resp_id"]

                    if resp_id == input_resp_id:
                        self.tdb.pop(key)
                        self.save_schevt_to_db("unregister", registered_event)
                        # 3. remove it from running_schedules and cancel it
                        future_event = self.running_schedules.pop(key, None)
                        future_event.cancel()
                        found_count += 1

                        log_info(f"handle_event unregistered: {key}({resp_id})")

        except Exception as ex:
            raise ex

        return {"count": found_count}

    def delete_schedules(self, input_resp_id: str = "", input_group_id: str = ""):
        try:
            if type(input_resp_id) is not str or input_resp_id == "":
                raise Exception(f"input_resp_id is not available.. {input_resp_id}")

            # 1. get all key-value data in the localqueue and find the specified name using for-iteration
            key_value_events = self.tdb.get_key_value_list()
            log_debug(f"*** get_key_value_list: {key_value_events}")

            found_count = 0
            if len(key_value_events):
                for key, registered_event in key_value_events:
                    # 2. pop the event from localqueue if found
                    resp_id = registered_event["resp_id"]
                    client_info = registered_event["client"]

                    if (input_resp_id and (resp_id == input_resp_id)) or (
                        input_group_id and (input_group_id == client_info["group"])
                    ):
                        self.tdb.pop(key)
                        self.save_schevt_to_db("unregister", registered_event)
                        # 3. remove it from running_schedules and cancel it
                        future_event = self.running_schedules.pop(key, None)
                        future_event.cancel()
                        found_count += 1

                        log_info(f"handle_event unregistered: {key}({resp_id})")

        except Exception as ex:
            raise ex

        return {"count": found_count}

    def get_schedules(
        self, resp_id: str, group: str, application: str, dlq: bool = False
    ):
        list_item = list()

        # 1. fetch the dlq flag, True or False
        client_application = application
        client_group = group

        try:
            # 2. gather all key-value data from the localqueue
            key_value_events = self.tdb.get_key_value_list(dlq)
            list_item = [
                schedule
                for _, schedule in key_value_events
                if (
                    not client_application
                    or client_application == schedule["client"]["application"]
                )
                and (not client_group or client_group == schedule["client"]["group"])
                and (not resp_id or resp_id == schedule["resp_id"])
            ]
        except Exception as ex:
            raise ex

        return list_item

    def get_groups(self):
        group_list = list()
        try:
            key_value_events = self.tdb.get_key_value_list(False)
            for _, value in key_value_events:
                client_info = value["client"]
                if not client_info["group"] in group_list:
                    group_list.append(client_info["group"])

        except Exception as ex:
            raise ex

        return group_list

    def delete_group(self, group_id: str) -> dict:
        try:
            key_value_events = self.tdb.get_key_value_list(False)
            for _, value in key_value_events:
                client_info = value["client"]
                if not client_info["group"] in group_list:
                    group_list.append(client_info["group"])

        except Exception as ex:
            raise ex

    def register_next(self, schedule_event):
        try:
            client_info = schedule_event["client"]
            # 1. check if scheluer event type is
            if ScheduleEventType.is_recurring(schedule_event["type"]):
                # 2. calculate the next timestamp and delay based on schedule_event
                (next_time, delay) = ScheduleEventType.get_next_and_delay(
                    schedule_event
                )

                input_data_task = schedule_event["task"]

                # 3. reset the retry count
                input_data_task["retry_count"] = 0

                # 4. set the next timestamp
                input_data_task["next"] = next_time

                # 5. set the evetn to the localqueue
                self.tdb.put(client_info["key"], schedule_event)
                self.save_schevt_to_db("register", schedule_event)

                handle_event_future = asyncio.run_coroutine_threadsafe(
                    self.handle_event(client_info["key"], schedule_event.copy(), delay),
                    asyncio.get_event_loop(),
                )
                self.running_schedules[client_info["key"]] = handle_event_future
            else:
                # pop this schedule event if it is not ono of recurrring schedule types.
                self.tdb.pop(client_info["key"])
                self.running_schedules.pop(client_info["key"], None)
        except Exception as ex:
            raise ex

    def save_schevt_to_db(self, event, schedule_event):
        try:
            task_info = schedule_event.get("task", {})
            client_info = schedule_event.get("client", {})
            if task_info:
                hischeck = task_info.get("history_check", False)
                if hischeck:
                    (host, port, id, pw, db) = Config.db()
                    initialize_global_database(id, pw, host, port, db)
                    with get_session() as db_session:
                        schevt_history = ScheduleEventHistory(
                            event=event,
                            name=client_info.get("name"),
                            key=client_info.get("key"),
                            group=client_info.get("group"),
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

    def reset(self):
        try:
            reset_result = dict()

            # reset the schedule queue
            count = 0
            key_value_list = self.tdb.get_key_value_list(False)
            for key, value in key_value_list:
                self.save_schevt_to_db("deleted", value)
                self.tdb.pop(key, False)
                future_event = self.running_schedules.pop(key, None)
                future_event.cancel() if future_event else None
                count += 1
            reset_result["schevt"] = count

            # reset the dead letter queue(dlq)
            key_list = self.tdb.get_key_list(True)
            count = 0
            for key in key_list:
                self.tdb.pop(key, True)
                count += 1
            reset_result["dlq"] = count
        except Exception as ex:
            raise ex

        return reset_result

    async def handle_event(self, key, schedule_event, delay):
        try:
            log_info(f"handle_event start: {key}")

            # 1. put it into the qeueue with the status 'waiting'
            task_info = schedule_event["task"]
            task_info["status"] = ScheduleTaskStatus.WAITING
            self.tdb.put(key, schedule_event)

            # 2. sleep with the input delay
            client_info = schedule_event["client"]
            log_debug(f"*** before sleep({key})")
            await asyncio.sleep(delay)
            log_debug(f"*** after sleep({key})")

            # 3. run a task based on task parameters
            task_cls = TaskManager.get(task_info["type"])
            task = task_cls()

            task.connect(**task_info)
            res = await task.run(**schedule_event)
            log_debug(f"handle_event done: {key}, res: {str(res)}")

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
                task_info["status"] = ScheduleTaskStatus.FAILED
                log_debug(f"got the wrong response of the task({key})")
                raise Exception(f"got the wrong response of the task({key})")

        except Exception as ex:
            log_error(f"Exception: {ex}")

            log_debug(f'failed_policy: {task_info.get("failed_policy")}')

            # 0. set the lastRun
            task_info["lastRun"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            # 1. in case that 'failed_policy' == "retry"
            if (
                task_info.get("failed_policy", "ignore") == "retry"
                or task_info.get("failed_policy", "ignore") == "retry_dlq"
            ):
                # 1.1 increase the retry count
                task_info["retry_count"] += 1
                task_info["status"] = ScheduleTaskStatus.RETRY
                task_info["lastRun"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                # 1.2 this event will be sent to DLQ if retry count limit is reached to the limit
                if task_info["retry_count"] >= task_info.get(
                    "max_retry_count", ScheduleEventHandler.TASK_RETRY_MAX
                ):
                    log_info(f"reached retry max count... {key}")

                    # 1.2.1 pop this schedule from the standard queue and put it into DLQ
                    task_info["status"] = ScheduleTaskStatus.FAILED
                    if task_info.get("failed_policy", "ignore") == "retry_dlq":
                        self.tdb.put(key, schedule_event, dlq=True)
                    self.tdb.pop(key)

                    # 1.2.2 update the schedule event dict and cancel it
                    future_event = self.running_schedules.pop(key, None)
                    future_event.cancel() if future_event else None
                # 1.3 retry one more..
                else:
                    # 1.3.1 put it into the queue with the changed status
                    task_info["status"] = ScheduleTaskStatus.RETRY
                    self.tdb.put(key, schedule_event)

                    # 1.3.2 run it again and update the schedule evnet dict.
                    handle_event_future = asyncio.run_coroutine_threadsafe(
                        self.handle_event(key, schedule_event.copy(), delay),
                        asyncio.get_event_loop(),
                    )
                    self.running_schedules[key] = handle_event_future
            # 2. in case that 'failed_policy' == "ignore"
            else:
                # 2.1 savd the event to history db with status 'failed' and udpate the schedule event dictionary
                self.save_schevt_to_db("failed", schedule_event)
                self.tdb.pop(key)
                future_event = self.running_schedules.pop(key, None)

                # 2.2 cancle the current event
                future_event.cancel() if future_event else None
