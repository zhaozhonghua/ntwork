import enum
import requests
import os

from common.utils import md5
from common.utils.json_util import store_json_in_file, get_json_data_from_file
from setting import SAPIENTIA_APP_IDENTIFIER


class SyncEvent(enum.Enum):
    SYNC_ROOM = "sync_room"
    SYNC_ROOM_MEMBER = "sync_room_member"
    SYNC_CHAT_RECORD = "sync_chat_record"


class WeWorkDataSync:
    sapientia_host = "https://chat.walnutpa.com"
    host = "http://localhost:8000"
    headers = {
        "Content-Type": "application/json"
    }

    def get_guid(self):
        url = f"{self.host}/client/guid/list"
        result = requests.post(url, headers=self.headers).json()
        data = result.get("data") or {}
        guid_list = data.get("guid_list")
        return guid_list[0] if guid_list else ""

    def get_rooms(self, page_num=1, page_size=500):
        guid = self.get_guid()
        if not guid:
            print("invalid get guid")
            raise ValueError("invalid get guid")
        url = f"{self.host}/room/get_rooms"
        params = {
            "guid": guid,
            "page_num": page_num,
            "page_size": page_size
        }
        result = requests.post(url, json=params, headers=self.headers).json()
        return result.get("data")

    def sync_rooms_notice(self, event, data):
        url = f"{self.sapientia_host}/api/app/utv/v1/sync/wework/data"
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Token {SAPIENTIA_APP_IDENTIFIER}"
        }
        params = {
            "event": event,
            "data": data,
        }
        result = requests.post(url, json=params, headers=headers).json()
        print("sync_rooms_notice result:", result)

    def sync_rooms(self):
        page_num, page_size = 1, 500
        cache_room_json_file = f"C:/www/ntwork/data/{page_num}_{page_size}_rooms.json"
        cache_rooms = {}
        if os.path.exists(cache_room_json_file):
            cache_rooms = get_json_data_from_file(cache_room_json_file)
        rooms = self.get_rooms(page_num, page_size)
        if cache_rooms:
            last_md5 = md5(cache_rooms)
            this_md5 = md5(rooms)
            if last_md5 == this_md5:
                print("last_md5 and this_md5 same")
                return
        store_json_in_file(rooms, cache_room_json_file)
        self.sync_rooms_notice(SyncEvent.SYNC_ROOM.value, rooms)
        return rooms

    def sync(self):
        self.sync_rooms()


if __name__ == '__main__':
    w = WeWorkDataSync()
    w.sync()
