# -*- coding: utf-8 -*-

import requests

from fastapi_example.setting import SAPIENTIA_APP_IDENTIFIER, SAPIENTIA_HOST


class SapientiaApi:

    def __init__(self):
        self.host = "http://localhost:8000"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {SAPIENTIA_APP_IDENTIFIER}",
        }

    def sync_wework_event_data_notice(self, guid, message):
        url = f"{SAPIENTIA_HOST}/api/app/utv/v1/sync/wework/event/data"
        params = {
            "guid": guid,
            "message": message,
        }
        result = requests.post(url, json=params, headers=self.headers).json()
        return result

    def bot_reply(self, content, context_id, end_user):
        url = f"{SAPIENTIA_HOST}/api/app/utv/v1/agent/qa"
        params = {
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "context_id": context_id,
            "end_user": end_user
        }
        result = requests.post(url, json=params, headers=self.headers).json()
        return result.get("data", {}).get("answer", "")
