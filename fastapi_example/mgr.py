# -*- coding: utf-8 -*-
from typing import Dict, Union

import requests

import ntwork
from exception import ClientNotExists
from ntwork.utils.singleton import Singleton
from setting import SAPIENTIA_APP_IDENTIFIER, SAPIENTIA_HOST
from utils import generate_guid


def bot_reply(message):
    url = f"{SAPIENTIA_HOST}/api/app/utv/v1/agent/qa"
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Token {SAPIENTIA_APP_IDENTIFIER}"
    }
    data = message.get("data")
    conversation_id = data.get("conversation_id")
    context_id = conversation_id

    end_user = data.get("send_name")
    content = data.get("content")
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
    print(headers)
    print(params)
    result = requests.post(url, json=params, headers=headers).json()
    return result.get("data", {}).get("answer", "")


class ClientWeWork(ntwork.WeWork):
    guid: str = ""


class ClientManager(metaclass=Singleton):
    __client_map: Dict[str, ntwork.WeWork] = {}
    callback_url: str = ""

    def new_guid(self):
        """
        生成新的guid
        """
        while True:
            guid = generate_guid("wework")
            if guid not in self.__client_map:
                return guid

    def create_client(self):
        guid = self.new_guid()
        wework = ClientWeWork()
        wework.guid = guid
        self.__client_map[guid] = wework

        # 注册回调
        wework.on(ntwork.MT_ALL, self.__on_callback)
        wework.on(ntwork.MT_RECV_WEWORK_QUIT_MSG, self.__on_quit_callback)
        return guid

    def get_client(self, guid: str) -> Union[None, ntwork.WeWork]:
        client = self.__client_map.get(guid, None)
        if client is None:
            raise ClientNotExists(guid)
        return client

    def get_client_guid_list(self):
        return list(self.__client_map.keys())

    def remove_client(self, guid):
        if guid in self.__client_map:
            del self.__client_map[guid]

    def reply(self, wework, message):
        answer = bot_reply(message)
        print(answer)
        if answer:
            conversation_id = message.get("data").get("conversation_id")
            self.get_client(wework.guid).send_text(conversation_id, answer)

    def __on_callback(self, wework, message):
        if not self.callback_url:
            return
        self.reply(wework, message)

    def __on_quit_callback(self, wework):
        self.__on_callback(wework, {"type": ntwork.MT_RECV_WEWORK_QUIT_MSG, "data": {}})
