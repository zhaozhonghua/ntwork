# -*- coding: utf-8 -*-
import argparse
import codecs
import json
import os
import sys

import requests

from common.utils import md5
from common.utils.json_util import store_json_in_file, get_json_data_from_file
from fastapi_example.sapientia_api import SapientiaApi
from ntwork.const import send_type

# 设置标准输出为UTF-8编码
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class WeWorkDataSync:
    host = "http://localhost:8000"
    headers = {
        "Content-Type": "application/json"
    }
    skip_md5_check = False
    sap_api = SapientiaApi()

    def get_guid(self):
        url = f"{self.host}/client/guid/list"
        result = requests.post(url, headers=self.headers).json()
        data = result.get("data") or {}
        guid_list = data.get("guid_list")
        return guid_list[0] if guid_list else ""

    def get_rooms(self, guid, page_num=1, page_size=500):
        url = f"{self.host}/room/get_rooms"
        params = {
            "guid": guid,
            "page_num": page_num,
            "page_size": page_size
        }
        result = requests.post(url, json=params, headers=self.headers).json()
        return result.get("data")

    def get_room_members(self, guid, conversation_id, page_num, page_size):
        url = f"{self.host}/room/get_room_members"
        params = {
            "guid": guid,
            "conversation_id": conversation_id,
            "page_num": page_num,
            "page_size": page_size
        }
        result = requests.post(url, json=params, headers=self.headers).json()
        return result.get("data")

    def sync_rooms(self):
        guid = self.get_guid()
        if not guid:
            print("invalid get guid")
            raise ValueError("invalid get guid")
        page_num, page_size = 1, 500
        cache_room_json_file = f"C:/www/ntwork/data/{page_num}_{page_size}_rooms.json"
        cache_rooms = {}
        if os.path.exists(cache_room_json_file):
            cache_rooms = get_json_data_from_file(cache_room_json_file)
        rooms = self.get_rooms(guid, page_num, page_size)
        if cache_rooms:
            last_md5 = md5(json.dumps(cache_rooms))
            this_md5 = md5(json.dumps(rooms))
            if not self.skip_md5_check and last_md5 == this_md5:
                print("rooms last_md5 and this_md5 same")
                return
        store_json_in_file(rooms, cache_room_json_file)
        send_data = {
            "type": send_type.MT_GET_ROOMS_MSG,
            "message": rooms
        }
        self.sap_api.sync_wework_event_data_notice(guid, send_data)
        room_list = rooms.get("room_list") or []
        for room in room_list:
            conversation_id = room.get("conversation_id") or ""
            if not conversation_id:
                continue
            print("sync room members conversation_id:", conversation_id)
            room_members = self.sync_room_members(guid, conversation_id)
            print(room_members)
        return rooms

    def sync_room_members(self, guid, conversation_id):
        page_num, page_size = 1, 500
        room_id = conversation_id.replace(":", "_")
        cache_room_member_json_file = f"C:/www/ntwork/data/{room_id}_{page_num}_{page_size}_room_members.json"
        cache_room_members = {}
        if os.path.exists(cache_room_member_json_file):
            cache_room_members = get_json_data_from_file(cache_room_member_json_file)
        room_members = self.get_room_members(guid, conversation_id, page_num, page_size)
        print(room_members)
        if cache_room_members:
            last_md5 = md5(json.dumps(cache_room_members))
            this_md5 = md5(json.dumps(room_members))
            if not self.skip_md5_check and last_md5 == this_md5:
                print("room_members last_md5 and this_md5 same")
                return
        if room_members:
            store_json_in_file(room_members, cache_room_member_json_file)
            send_data = {
                "type": send_type.MT_GET_ROOM_MEMBERS_MSG,
                "message": room_members
            }
            self.sap_api.sync_wework_event_data_notice(guid, send_data)
        return room_members

    def sync(self):
        self.sync_rooms()


def get_args():
    parser = argparse.ArgumentParser(description="WeWorkDataSync")
    parser.add_argument("--skip_md5_check", default=False, action="store_true", help="skip_md5_check")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    print(args)
    w = WeWorkDataSync()
    w.skip_md5_check = args.skip_md5_check
    w.sync()
