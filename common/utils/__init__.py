import hashlib
import json
import uuid
import re


def underline2hump(underline_str):
    # 这里re.sub()函数第二个替换参数用到了一个匿名回调函数，回调函数的参数x为一个匹配对象，返回值为一个处理后的字符串
    sub = re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), underline_str)
    return sub


def hump2underline(hunp_str):
    # 匹配正则，匹配小写字母和大写字母的分界位置
    p = re.compile(r'([a-z]|\d)([A-Z])')
    # 这里第二个参数使用了正则分组的后向引用
    sub = re.sub(p, r'\1_\2', hunp_str).lower()
    return sub


def json_hump2underline(hump_json_str):
    if not hump_json_str:
        return hump_json_str

    attr_ptn = re.compile(r'"\s*(\w+)\s*"\s*:')
    # 使用hump2underline函数作为re.sub函数第二个参数的回调函数
    sub = re.sub(attr_ptn, lambda x: '"' + hump2underline(x.group(1)) + '" :', json.dumps(hump_json_str))
    return json.loads(sub)


def json_underline2hump(underline_json_str):
    if not underline_json_str:
        return underline_json_str

    attr_ptn = re.compile(r'"\s*(\w+)\s*"\s*:')
    sub = re.sub(attr_ptn, lambda x: '"' + underline2hump(x.group(1)) + '" :', json.dumps(underline_json_str))
    return json.loads(sub)


def is_english(line, threshold=0.75):
    chars = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)]
    if not line:
        return False
    count_total = len(line)
    count_chars = sum([1 if c in chars else 0 for c in line])
    if count_total == 0:
        return False
    char_percent = count_chars / float(count_total)
    return char_percent > threshold


def md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    return m.hexdigest()


def gen_uuid():
    return uuid.uuid4().hex


def gen_signature(timestamp, md5_key):
    if not timestamp or not md5_key:
        return ''
    signature = md5('{timestamp}{md5_key}'.format(timestamp=timestamp, md5_key=md5_key))
    return signature


def check_signature(signature, timestamp, md5_key):
    if not signature or not timestamp or not md5_key:
        return False

    _signature = md5('{timestamp}{md5_key}'.format(timestamp=timestamp, md5_key=md5_key))
    if signature == _signature:
        return True
    return False


class ObjectDict(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class MyJsonEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')

        return json.JSONEncoder.default(self, obj)
