from gql.gql_types import ScheduleTaskFailurePolicy, ScheduleTaskStatus


def convert_schedule_event_to_dict(schedule_event):
    schedule_dict = schedule_event.to_dict()
    schedule_task = schedule_dict.get("task")
    failed_policy = schedule_task.get("failed_policy", ScheduleTaskFailurePolicy.IGNORE)
    schedule_task["failed_policy"] = failed_policy.value
    status = schedule_task.get("status", ScheduleTaskStatus.IDLE)
    schedule_task["status"] = status.value
    return schedule_dict


def convert_schedule_event_to_dict(schedule_dict):
    pass
