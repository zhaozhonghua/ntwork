# -*- coding: utf-8 -*-
import random
import re
import copy
import time
import os
import uuid
from typing import Dict, Union

from fastapi.logger import logger

import ntwork
from exception import ClientNotExists
from ntwork.const import notify_type, send_type
from ntwork.utils.singleton import Singleton
from sapientia_api import SapientiaApi
from utils import generate_guid
from setting import SAPIENTIA_ACCOUNT_SECRET_KEY, SAPIENTIA_HOST


class ClientWeWork(ntwork.WeWork):
    guid: str = ""

    def wx_cdn_download(self, url: str, auth_key: str, aes_key: str, size: int, save_path):
        """
        下载wx类型的cdn文件，以https开头
        """
        data = {
            'url': url,
            'aes_key': aes_key,
            'auth_key': auth_key,
            'size': size,
            'save_path': save_path
        }
        return self._WeWork__send_sync(send_type.MT_WXCDN_DOWNLOAD_MSG, data)


class ClientManager(metaclass=Singleton):
    __client_map: Dict[str, ntwork.WeWork] = {}
    callback_url: str = ""
    login_user_id: str = ""

    sap_api = SapientiaApi(SAPIENTIA_HOST, SAPIENTIA_ACCOUNT_SECRET_KEY)

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
        return dict(
            guid_list=list(self.__client_map.keys()),
            login_user_id=self.login_user_id
        )

    def remove_client(self, guid):
        if guid in self.__client_map:
            del self.__client_map[guid]

    def download_cdn_file(self, client_wework, message, file_name):
        data = message["data"]
        aes_key = data["cdn"]["aes_key"]
        file_size = data["cdn"]["size"]

        # 获取当前工作目录，然后与文件名拼接得到保存路径
        directory = os.path.join(os.getcwd(), "tmp")
        # 如果目录不存在，则创建目录
        if not os.path.exists(directory):
            os.makedirs(directory)
        save_path = os.path.join(directory, file_name)

        # 下载文件到本地
        if "url" in data["cdn"].keys() and "auth_key" in data["cdn"].keys():
            url = data["cdn"]["url"]
            auth_key = data["cdn"]["auth_key"]
            # 下载wx类型的cdn文件，以https开头
            data = {
                'url': url,
                'auth_key': auth_key,
                'aes_key': aes_key,
                'size': file_size,
                'save_path': save_path
            }
            result = client_wework.wx_cdn_download(**data)
        elif "file_id" in data["cdn"].keys():
            if message["type"] == notify_type.MT_RECV_IMAGE_MSG:
                file_type = 2
            elif message["type"] == notify_type.MT_RECV_FILE_MSG:
                file_type = 5
            else:
                logger.warning("not exist file_id")
                return
            file_id = data["cdn"]["file_id"]
            result = client_wework.c2c_cdn_download(file_id, aes_key, file_size, file_type, save_path)
        else:
            logger.error(f"something is wrong, data: {data}")
            return
        # 输出下载结果
        msg = f"download_cdn_file result: {result}"
        logger.debug(msg)
        print(msg)

    def convert_message(self, wework, message):
        c_message = copy.deepcopy(message)
        client_wework = self.get_client(wework.guid)
        msg_type = c_message.get("type")
        if msg_type == notify_type.MT_RECV_IMAGE_MSG:
            download_file_name = f"{uuid.uuid4().hex}.jpg"
            self.download_cdn_file(client_wework, c_message, download_file_name)
        if msg_type == notify_type.MT_RECV_VOICE_MSG:
            pass
        if msg_type == notify_type.MT_RECV_FILE_MSG:
            pass
        if msg_type == notify_type.MT_RECV_VIDEO_MSG:
            pass
        return c_message

    def report_message(self, wework, message):
        try:
            c_message = self.convert_message(wework, message)
            self.sap_api.sync_wework_event_data_notice(wework.guid, c_message)
        except Exception as e:
            logger.exception(e)

    def reply(self, wework, message):
        receive_start_time = int(time.time())
        self.report_message(wework, message)
        logger.info("login_user_id:%s message:%s", self.login_user_id, message)
        msg_type = message.get("type")
        data = message.get("data") or {}
        conversation_id = data.get("conversation_id")
        receiver = data.get("receiver")
        sender = data.get("sender")
        at_list = data.get("at_list")
        end_user = data.get("send_name")
        content = data.get("content")
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
        if "@" in content:
            content = re.sub(r'@\S+\s*', '', content)
        answer = self.sap_api.bot_reply(content, conversation_id, end_user)
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
