from datetime import datetime, timezone
from croniter import croniter
from local_crontab import Converter
import pytz


def calculate_cron_unit(cron_element):
    slash_splits = cron_element.split("/")

    conv_seconds = 0
    if len(slash_splits) == 2:
        conv_seconds = int(slash_splits[1])
    elif cron_element == "*":
        conv_seconds = 1
    else:
        conv_seconds = int(cron_element)

    return conv_seconds


# def convert_cron_to_utc(schedule, tz):
#     """
#     convert cronjob format of node.js to that of python modules.

#     """
#     base = datetime.now(timezone.utc)
#     cron_elements = schedule.split() if type(schedule) is str else str(schedule).split()


#     if len(cron_elements) == 5:
#         utc_cron = Converter(schedule, tz).to_utc_cron()
#         utc_cron_elements = utc_cron.split()

#         # change hour and day
#         cron_elements[1] = utc_cron_elements[1]
#         cron_elements[2] = utc_cron_elements[2]
#     elif len(cron_elements) == 6:

#     else:
#         pass
