from datetime import date
from urllib.parse import urlencode
from requests import exceptions, get
from tool import retry
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)
from random import randint
from time import sleep

from config import PROGRESS, WARNING
from encrypt_params import get_a_bogus
from tool import ColorfulConsole
from config import Settings


class Acquire():
    post_api = 'https://www.douyin.com/aweme/v1/web/aweme/post/'

    def __init__(self, settings: Settings, console: ColorfulConsole):
        self.console = console
        self.settings = settings

    def request_items(self, sec_user_id: str, earliest: date):
        '''获取账号作品数据并返回'''
        items = []
        with self.__progress_object() as progress:
            task_id = progress.add_task('正在获取账号主页数据', total=None)
            self.cursor = 0
            self.finished = False
            while not self.finished:
                progress.update(task_id)
                if (items_page := self.__request_items_page(sec_user_id)):
                    items.extend(items_page)
                    self.__early_stop(earliest)
        self.console.print(f'当前账号获取作品数量: {len(items)}')
        return items

    def __progress_object(self):
        return Progress(
            TextColumn('[progress.description]{task.description}', style=PROGRESS, justify='left'),
            '•',
            BarColumn(bar_width=20),
            '•',
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        )

    @retry
    def __request_items_page(self, sec_user_id: str):
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
        self.__deal_url_params(params)
        if not (data := self.__send_get(params=params)):
            self.console.print('获取账号作品数据失败', style=WARNING)
            self.finished = True
        else:
            try:
                if (items_page := data['aweme_list']) is None:
                    self.console.print(
                        '该账号为私密账号，需要使用登录后的 Cookie，且登录的账号需要关注该私密账号',
                        style=WARNING)
                    self.finished = True
                else:
                    self.cursor = data['max_cursor']
                    self.finished = not data['has_more']
                    return items_page
            except KeyError:
                self.console.print(f'账号作品数据响应内容异常: {data}', style=WARNING)
                self.finished = True

    def __send_get(self, params):
        try:
            response = get(
                self.post_api,
                params=params,
                timeout=self.settings.timeout,
                headers=self.settings.headers)
            self.__wait()
        except (
                exceptions.ProxyError,
                exceptions.SSLError,
                exceptions.ChunkedEncodingError,
                exceptions.ConnectionError,
        ):
            self.console.print(f'网络异常，请求 {self.post_api}?{urlencode(params)} 失败', style=WARNING)
            return
        except exceptions.ReadTimeout:
            self.console.print(f'网络异常，请求 {self.post_api}?{urlencode(params)} 超时', style=WARNING)
            return
        try:
            return response.json()
        except exceptions.JSONDecodeError:
            if response.text:
                self.console.print(f'响应内容不是有效的 JSON 格式：{response.text}', style=WARNING)
            else:
                self.console.print(
                    '响应内容为空，可能是接口失效或者 Cookie 失效，请尝试更新 Cookie', style=WARNING)

    @staticmethod
    def __wait():
        sleep(randint(15, 45)/10)

    def __deal_url_params(self, params: dict, number: int = 8):
        '''添加 msToken、X-Bogus'''
        cookies = self.settings.cookies
        if isinstance(cookies, dict) and 'msToken' in cookies:
            params['msToken'] = cookies['msToken']
        params['a_bogus'] = get_a_bogus(params)

    def __early_stop(self, earliest: date):
        '''如果获取数据的发布日期已经早于限制日期，就不需要再获取下一页的数据了'''
        if earliest > date.fromtimestamp(self.cursor / 1000):
            self.finished = True
