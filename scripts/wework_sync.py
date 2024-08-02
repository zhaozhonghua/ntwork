import requests


class WeWorkDataSync:

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

    def get_rooms(self):
        guid = self.get_guid()
        if not guid:
            print("invalid get guid")
            raise ValueError("invalid get guid")
        url = f"{self.host}/room/get_rooms"
        params = {
            "guid": guid,
            "page_num": 1,
            "page_size": 500
        }
        result = requests.post(url, json=params, headers=self.headers).json()
        data = result.get("data") or {}
        room_list = data.get("room_list")
        print(room_list)
        return room_list

    def sync(self):
        self.get_rooms()


if __name__ == '__main__':
    w = WeWorkDataSync()
    w.sync()
