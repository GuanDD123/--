from os.path import (
    join as join_path,
    exists
)
from json import dump, load
from json.decoder import JSONDecodeError
from re import match
from os import makedirs
from copy import deepcopy
from types import MappingProxyType
from datetime import date, timedelta, datetime
from rich import print

from .constant import (
    PROJECT_ROOT,
    RED, YELLOW, GREEN,
    ENCODE,
    USER_AGENT
)


class Settings:
    file = join_path(PROJECT_ROOT, 'settings.json')  # 配置文件
    default_settings = MappingProxyType({
        'accounts': [
            {
                'mark': '账号标识，可以设置为空字符串',
                'url': '账号主页链接',
                'earliest': '作品最早发布日期',
                'latest': '作品最晚发布日期'
            },
        ],
        'save_folder': '',
        'cookies': {}
    })

    def __init__(self) -> None:
        self.name_format = ('create_time', 'id', 'type', 'desc')  # 'id', 'desc', 'create_time', 'nickname', 'uid', 'mark', 'type'
        self.date_format = '%Y-%m-%d'
        self.split = '-'
        self.chunk = 1024 ** 2  # 每次从服务器接收的数据块大小
        self.timeout = 10
        self.headers = {'Referer': 'https://www.douyin.com/', 'User-Agent': USER_AGENT}
        self.cookies = None

    def check(self):
        '''检查配置文件内容，并将配置保存到 self.settings 属性；
        若配置文件有误，则返回 False；
        如果没有配置文件，则创建默认配置文件；
        若缺少参数，询问是否创建默认配置文件'''
        self.settings = self._read()
        self.quit = False
        if self.settings:
            if set(self.default_settings.keys()) <= (set(self.settings.keys())):
                self.accounts = deepcopy(self.settings['accounts'])
                self._check_accounts()
                self.save_folder = self.settings['save_folder']
                self._check_save_folder('save_folder')
                self.cookies = self.settings['cookies']
                self._check_cookies('cookies')
            else:
                print(f'[{RED}]配置文件 settings.json 缺少必要的参数！')
                self.quit = True
                if input('是否生成默认配置文件？Y/N：').lower() == 'y':
                    self._create()
        else:
            self.quit = True
        return False if self.quit else True

    def _check_save_folder(self, key: str):
        if not self.save_folder:
            print(f'[{YELLOW}]参数 {key} 未设置，将使用默认存储位置 {PROJECT_ROOT}！')
            self.save_folder = PROJECT_ROOT
        elif not isinstance(self.save_folder, str):
            print(f'[{YELLOW}]参数 {key} 值 {self.save_folder} 格式错误，将使用默认存储位置 {PROJECT_ROOT}！')
            self.save_folder = PROJECT_ROOT
        elif not exists(self.save_folder):
            makedirs(self.save_folder, exist_ok=True)

    def _read(self):
        '''读取配置文件并返回配置内容'''
        if exists(self.file):
            try:
                with open(self.file, encoding=ENCODE) as f:
                    return load(f)
            except JSONDecodeError:
                print(f'[{RED}]配置文件 settings.json 格式错误，请检查 JSON 格式！')
        else:
            self._create()

    def _create(self):
        '''创建默认配置文件'''
        with open(self.file, 'w', encoding=ENCODE) as f:
            dump(dict(self.default_settings), f, indent=4, ensure_ascii=False)
        print(f'[{GREEN}]创建默认配置文件 settings.json 成功！')

    def _check_accounts(self):
        for account in self.accounts:
            account['sec_user_id'] = self._extract_sec_user_id(account['mark'], account['url'])
            account['earliest_date'] = self._generate_date_earliest(account['earliest'])
            account['latest_date'] = self._generate_date_latest(account['latest'])
            if self.quit:
                break

    def _extract_sec_user_id(self, mark: str, url: str):
        sec_user_id = match(
            r'https://www\.douyin\.com/user/([A-Za-z0-9_-]+)(\?.*)?', url).group(1)
        if sec_user_id:
            return sec_user_id
        else:
            print(f'[{RED}]参数 accounts 中账号 {mark} 的 url {url} 错误，提取 sec_user_id 失败！')
            self.quit = True

    def _generate_date_earliest(self, date_: str):
        if not date_:
            return date(2016, 9, 20)
        else:
            try:
                return datetime.strptime(date_, '%Y/%m/%d').date()
            except ValueError:
                print(f'[{YELLOW}]作品最早发布日期 {date_} 无效')
                return date(2016, 9, 20)

    def _generate_date_latest(self, date_: str):
        if not date_:
            return date.today() - timedelta(days=1)
        else:
            try:
                return datetime.strptime(date_, '%Y/%m/%d').date()
            except ValueError:
                print(f'[{YELLOW}]作品最晚发布日期无效 {date_}')
                return date.today() - timedelta(days=1)

    def _check_cookies(self, key: str):
        if not isinstance(self.cookies, dict):
            print(f'[{YELLOW}]参数 {key} 格式错误，请重新设置！')
            self.cookies = {}

    def save(self):
        '''将 self.settings 覆写到配置文件'''
        self.settings['cookies'] = self.cookies
        with open(self.file, 'w', encoding=ENCODE) as f:
            dump(self.settings, f, indent=4, ensure_ascii=False)
        print(f'[{GREEN}]保存配置成功！')
