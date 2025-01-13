from datetime import date
from urllib.parse import urlencode
from requests import exceptions, get
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)
from random import randint
from time import sleep
from rich import print

from ..config import MAGENTA, YELLOW, TIMEOUT
from ..encrypt_params import get_a_bogus
from ..tool import retry
from ..config import Settings


class Acquire():
    post_api = 'https://www.douyin.com/aweme/v1/web/aweme/post/'

    def __init__(self, settings: Settings):
        self.settings = settings

    def request_items(self, sec_user_id: str, earliest: date):
        '''获取账号作品数据并返回'''
        items = []
        with self._progress_object() as progress:
            task_id = progress.add_task('正在获取账号主页数据', total=None)
            self.cursor = 0
            self.finished = False
            while not self.finished:
                progress.update(task_id)
                if (items_page := self._request_items_page(sec_user_id)):
                    if not items_page == [None]:
                        items.extend(items_page)
                    self._early_stop(earliest)
        return items

    def _progress_object(self):
        return Progress(
            TextColumn('[progress.description]{task.description}', style=MAGENTA, justify='left'),
            '•',
            BarColumn(bar_width=20),
            '•',
            TimeElapsedColumn(),
            transient=True,
        )

    @retry
    def _request_items_page(self, sec_user_id: str):
        '''获取单页作品数据，更新 self.cursor'''
        params = {
            'device_platform': 'webapp',
            'aid': '6383',
            'channel': 'channel_pc_web',
            'sec_user_id': sec_user_id,
            'max_cursor': self.cursor,
            'locate_query': 'false',
            'show_live_replay_strategy': '1',
            'need_time_list': '0' if self.cursor else '1',
            'time_list_query': '0',
            'whale_cut_token': '',
            'cut_version': '1',
            'count': '18',
            'publish_video_strategy_type': '2',
            'pc_client_type': '1',
            'version_code': '170400',
            'version_name': '17.4.0',
            'cookie_enabled': 'true',
            'platform': 'PC',
            'downlink': '10',
        }
        self._deal_url_params(params)
        if not (data := self._send_get(params=params)):
            print(f'[{YELLOW}]获取账号作品数据失败')
            self.finished = True
        else:
            try:
                if (items_page := data['aweme_list']) is None:
                    print(f'[{YELLOW}]该账号为私密账号，需要使用登录后的 Cookie，且登录的账号需要关注该私密账号')
                    self.finished = True
                else:
                    self.cursor = data['max_cursor']
                    self.finished = not data['has_more']
                    return items_page or [None]
            except KeyError:
                print(f'[{YELLOW}]账号作品数据响应内容异常: {data}')
                self.finished = True

    def _send_get(self, params):
        '''返回 json 格式数据'''
        try:
            response = get(
                self.post_api,
                params=params,
                timeout=TIMEOUT,
                headers=self.settings.headers)
            self._wait()
        except (
                exceptions.ProxyError,
                exceptions.SSLError,
                exceptions.ChunkedEncodingError,
                exceptions.ConnectionError,
        ):
            print(f'[{YELLOW}]网络异常，请求 {self.post_api}?{urlencode(params)} 失败')
            return
        except exceptions.ReadTimeout:
            print(f'[{YELLOW}]网络异常，请求 {self.post_api}?{urlencode(params)} 超时')
            return
        try:
            return response.json()
        except exceptions.JSONDecodeError:
            if response.text:
                print(f'[{YELLOW}]响应内容不是有效的 JSON 格式：{response.text}')
            else:
                print(f'[{YELLOW}]响应内容为空，可能是接口失效或者 Cookie 失效，请尝试更新 Cookie')

    @staticmethod
    def _wait():
        sleep(randint(15, 45)/10)

    def _deal_url_params(self, params: dict, number: int = 8):
        '''添加 msToken、X-Bogus'''
        if 'msToken' in self.settings.cookies:
            params['msToken'] = self.settings.cookies['msToken']
        params['a_bogus'] = get_a_bogus(params)

    def _early_stop(self, earliest: date):
        '''如果获取数据的发布日期已经早于限制日期，就不需要再获取下一页的数据了'''
        if earliest > date.fromtimestamp(self.cursor / 1000):
            self.finished = True
