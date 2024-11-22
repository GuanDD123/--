from requests import (
    post,
    exceptions
)
from rich import print

from ..config import USER_AGENT, RED
from ..tool import retry


HEADERS = {'User-Agent': USER_AGENT}



@retry
def send_post(url: str, headers: dict, data: str):
    try:
        return post(url, data=data, timeout=10, headers=headers)
    except (
            exceptions.ProxyError,
            exceptions.SSLError,
            exceptions.ChunkedEncodingError,
            exceptions.ConnectionError,
            exceptions.ReadTimeout,
    ):
        return


def extract_value(response_headers: dict, key: str):
    '''从 response_headers['Set-Cookie'] 中，提取第一个键对应的值'''
    set_cookie = response_headers.get('Set-Cookie')
    if set_cookie:
        try:
            value = set_cookie.split('; ')[0].split('=', 1)
            return {value[0]: value[1]}
        except IndexError:
            print(f'[{RED}]获取 {key} 参数失败！')
