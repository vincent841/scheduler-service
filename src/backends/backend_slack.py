import json
import requests


class ENSBackendSlack:
    def name(self):
        return "slack"

    def fire(self, **kargs):
        self.slack_url = kargs["url"]
        self.slack_msg = dict()
        self.slack_msg["channel"] = kargs["channel"]
        self.slack_msg["username"] = "ENS Backend"
        self.slack_msg["text"] = kargs["text"]
        self.slack_msg["icon_emoji"] = ":heavy-check-mark:"

        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        requests.post(self.slack_url, headers=headers, data=json.dumps(self.slack_msg))
