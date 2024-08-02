import datetime
import decimal
import json
import re


def from_string_extract_json(text, json_type="object"):
    """
    从字符串中抽取json数据
    :param text:
    :param json_type: object|array
    example:
        str = 候选人的回答内容并没有回答问题，因此得分为0分。以下是面试评估结果：{"综合得分": 0, "综合评价": "候选人没有回答问题。"}sss
        > from_string_extract_json(str)
        {"综合得分": 0, "综合评价": "候选人没有回答问题。"}
    :return:
    """
    match_start_char = "{" if json_type == "object" else "["
    match_end_char = "}" if json_type == "object" else "]"
    left = text.find(match_start_char)
    right = text.rfind(match_end_char)
    if left == -1 or right == -1:
        return
    return json.loads(text[left: right+1])


def store_json_in_file(store_data, file_name, ensure_ascii=False):
    """
    将json数据存储到文件中
    :param store_data:
    :param file_name: /xx/xxx/xx.json
    :param ensure_ascii:
    :return:
    """
    with open(file_name, 'w', encoding='utf-8') as p_file:
        json.dump(store_data, p_file, ensure_ascii=ensure_ascii)


def get_json_data_from_file(file_name):
    """
    从文件中获取json数据
    :param file_name: /xx/xxx/xx.json
    :return:
    """
    with open(file_name, 'r', encoding='utf-8') as p_file:
        return json.load(p_file)


class JSONEncoder(json.JSONEncoder):
    """
    指定非内置 JSON serializable 的类型应该如何转换

    不符合JSON规范的类型包括：
        decimal.Decimal,
        datetime.datetime,
        datetime.date
    """
    def default(self, o):
        if isinstance(o, bytes):
            return str(o, encoding='utf-8')
        elif isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, datetime.datetime):
            return o.__str__()
        elif isinstance(o, datetime.date):
            return o.__str__()
        return super().default(self, o)


class LazyJSONDecoder(json.JSONDecoder):
    """
    https://stackoverflow.com/questions/65910282/jsondecodeerror-invalid-escape-when-parsing-from-python
    JSONDecodeError; Invalid /escape when parsing from Python
    """
    def decode(self, s, **kwargs):
        regex_replacements = [
            (re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2'),
            (re.compile(r',(\s*])'), r'\1'),
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)
