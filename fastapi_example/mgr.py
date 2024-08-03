# -*- coding: utf-8 -*-
import random
import re
import time
from typing import Dict, Union

import requests
from fastapi.logger import logger

import ntwork
from exception import ClientNotExists
from ntwork.const import notify_type
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
    if "@" in content:
        content = re.sub(r'@\S+\s*', '', content)
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
    result = requests.post(url, json=params, headers=headers).json()
    return result.get("data", {}).get("answer", "")


class ClientWeWork(ntwork.WeWork):
    guid: str = ""


class ClientManager(metaclass=Singleton):
    __client_map: Dict[str, ntwork.WeWork] = {}
    callback_url: str = ""
    login_user_id: str = ""

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
        receive_start_time = int(time.time())
        logger.info("login_user_id:%s message:%s", self.login_user_id, message)
        msg_type = message.get("type")
        conversation_id = message.get("data").get("conversation_id")
        receiver = message.get("data").get("receiver")
        sender = message.get("data").get("sender")
        at_list = message.get("data").get("at_list")
        if msg_type == notify_type.MT_USER_LOGIN_MSG:
            login_user_id = message.get("data").get("user_id")
            self.login_user_id = login_user_id
            return
        if msg_type not in [notify_type.MT_RECV_TEXT_MSG]:
            return
        at_user_ids = [at["user_id"] for at in at_list]
        if self.login_user_id not in at_user_ids:
            return
        if receiver != self.login_user_id:
            return
        answer = bot_reply(message)
        logger.info("answer:%s", answer)
        if not answer:
            return
        reply_content = f" {answer}"
        diff = int(time.time()) - receive_start_time
        if diff < 10:
            wait_seconds = random.randint(3, 8)
            logger.info("wait_seconds:%s", wait_seconds)
            time.sleep(wait_seconds)
        send_at_list = [sender]
        self.get_client(wework.guid).send_room_at_msg(conversation_id, reply_content, send_at_list)

    def __on_callback(self, wework, message):
        try:
            self.reply(wework, message)
        except Exception as e:
            print(e)

    def __on_quit_callback(self, wework):
        self.__on_callback(wework, {"type": ntwork.MT_RECV_WEWORK_QUIT_MSG, "data": {}})
