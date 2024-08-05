# -*- coding: utf-8 -*-

import requests

from fastapi_example.setting import SAPIENTIA_ACCOUNT_SECRET_KEY, SAPIENTIA_HOST


class SapientiaApi:

    def __init__(self):
        self.host = SAPIENTIA_HOST
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {SAPIENTIA_ACCOUNT_SECRET_KEY}",
        }

    def sync_wework_event_data_notice(self, guid, message):
        url = f"{self.host}/api/app/utv/v1/sync/wework/event/data"
        params = {
            "guid": guid,
            "message": message,
        }
        result = requests.post(url, json=params, headers=self.headers).json()
        return result

    def get_group_release(self, conversation_id):
        url = f"{self.host}/api/app/utv/v1/wework/group/release"
        params = {
            "conversation_id": conversation_id,
        }
        result = requests.post(url, json=params, headers=self.headers).json()
        data = result.get("data") or {}
        return data.get("identifier")

    def bot_reply(self, content, context_id, end_user):
        release_identifier = self.get_group_release(context_id)
        if not release_identifier:
            return
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {release_identifier}",
        }

        url = f"{self.host}/api/app/utv/v1/agent/qa"
        params = {
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "context_id": context_id,
            "end_user": end_user,
            "source": 6
        }
        result = requests.post(url, json=params, headers=headers).json()
        return result.get("data", {}).get("answer", "")
