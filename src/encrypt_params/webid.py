from requests import exceptions
from json import dumps
from rich import print

from .general import send_post
from ..config import USER_AGENT, RED


class WebID:

    @staticmethod
    def get_web_id(user_agent: str = USER_AGENT):
        api = 'https://mcs.zijieapi.com/webid'
        headers = {'User-Agent': user_agent}
        data = {
            'app_id': 6383,
            'url': 'https://www.douyin.com/',
            'user_agent': '{user_agent}',
            'referer': 'https://www.douyin.com/',
            'user_unique_id': ''
        }
        try:
            if response := send_post(api, headers, dumps(data)):
                return response.json().get('web_id')
            raise KeyError
        except (exceptions.JSONDecodeError, KeyError):
            print(f'[{RED}]获取 webid 参数失败！')
