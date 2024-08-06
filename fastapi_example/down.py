import os.path
import time
import requests
from xdg import get_download_dir
from models import SendMediaReqModel


def get_local_path(model: SendMediaReqModel):
    if os.path.isfile(model.file_path):
        return model.file_path
    if not model.url:
        return None
    data = requests.get(model.url).content
    temp_file = os.path.join(get_download_dir(), str(time.time_ns()))
    temp_file = os.path.join(os.getcwd(), temp_file)
    print(temp_file)
    with open(temp_file, 'wb') as fp:
        fp.write(data)
    return temp_file


def download_video(url, filename):
    # 确定保存视频的目录
    directory = os.path.join(os.getcwd(), "tmp")
    # 如果目录不存在，则创建目录
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 下载视频
    response = requests.get(url, stream=True)
    total_size = 0
    video_path = os.path.join(directory, f"{filename}.mp4")
    with open(video_path, 'wb') as f:
        for block in response.iter_content(1024):
            total_size += len(block)
            # 如果视频的总大小超过30MB (30 * 1024 * 1024 bytes)，则停止下载并返回
            if total_size > 30 * 1024 * 1024:
                return None
            f.write(block)
    return video_path
