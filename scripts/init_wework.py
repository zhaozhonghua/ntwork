import requests


class InitWeWork:
    host = "http://localhost:8000"
    headers = {
        "Content-Type": "application/json"
    }

    def gen_guid(self):
        url = f"{self.host}/client/create"
        result = requests.post(url, headers=self.headers).json()
        data = result.get("data") or {}
        guid = data.get("guid")
        return guid

    def open_wework(self, guid):
        url = f"{self.host}/client/open"
        params = {
            "guid": guid,
            "smart": True,
            "show_login_qrcode": True
        }
        result = requests.post(url, json=params, headers=self.headers).json()
        data = result.get("data") or {}
        return data

    def init(self):
        guid = self.gen_guid()
        if not guid:
            raise ValueError("gen guid error")
        result = self.open_wework(guid)
        print("open_wework:", result)


if __name__ == '__main__':
    i = InitWeWork()
    i.init()
