import json
import requests

from service.service_abstract import Serivce


class ServiceSlack(Serivce):
    def __init__(self):
        pass

    def get_name(self):
        return "slack"

    def connect(self, **kargs):
        pass

    def run(self, **kargs):
        self.slack_url = kargs["url"]
        self.slack_msg = dict()
        self.slack_msg["channel"] = kargs["channel"]
        self.slack_msg["username"] = "ENS Backend"
        self.slack_msg["text"] = kargs["text"]
        self.slack_msg["icon_emoji"] = ":heavy-check-mark:"

        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        requests.post(self.slack_url, headers=headers, data=json.dumps(self.slack_msg))
