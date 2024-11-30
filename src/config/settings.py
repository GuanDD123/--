from os.path import (
    join as join_path,
    exists
)
from json import dump, load
from json.decoder import JSONDecodeError
from re import match
from os import makedirs
from copy import deepcopy
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
    default_settings = {
        'accounts': [
            {
                'mark': '账号标识，可以设置为空字符串',
                'url': '账号主页链接',
                'earliest': '作品最早发布日期',
                'latest': '作品最晚发布日期'
            },
        ],
        'cookies': {},
        'save_folder': '',
        'download_videos': 'True',
        'download_images': 'False',
        'name_format': 'create_time id type desc',
        'split': '-',
        'date_format': '%Y-%m-%d'
    }

    def __init__(self) -> None:
        self.headers = {'Referer': 'https://www.douyin.com/', 'User-Agent': USER_AGENT}

    def load_settings(self):
        '''读取配置文件内容，并将配置保存到 self.settings 属性；
        如果没有配置文件，则创建默认配置文件；
        若缺少参数，询问是否创建默认配置文件'''
        self.settings = self._read()
        if self.settings:
            if set(self.default_settings.keys()) <= (set(self.settings.keys())):
                self._load_accounts()
                self._load_cookies()
                self._load_save_folder()
                self._load_download()
                self._load_name()
            else:
                print(f'[{RED}]配置文件 settings.json 缺少必要的参数！')
                if input('是否生成默认配置文件？Y/N：').lower() == 'y':
                    self._create()

    def save(self):
        '''将 self.settings 覆写到配置文件'''
        with open(self.file, 'w', encoding=ENCODE) as f:
            dump(self.settings, f, indent=4, ensure_ascii=False)
        print(f'[{GREEN}]保存配置成功！')

    def _load_download(self):
        self.download_videos = True if str(self.settings['download_videos']).lower() != 'false' else False
        self.download_images = True if str(self.settings['download_images']).lower() != 'false' else False

    def _load_name(self):
        self.name_format = str(self.settings['name_format']).split()
        if (not self.name_format) or (
                not set(self.name_format) <= {'id', 'desc', 'create_time', 'type'}):
            self.name_format = ['create_time', 'id', 'type', 'desc']

        self.split = str(self.settings['split']) or '-'
        self.date_format = str(self.settings['date_format']) or '%Y-%m-%d'

    def _load_save_folder(self):
        self.save_folder = str(self.settings['save_folder'])
        if not self.save_folder:
            print(f'[{YELLOW}]参数 "save_folder" 未设置，将使用默认存储位置 {PROJECT_ROOT}！')
            self.save_folder = PROJECT_ROOT
        elif not exists(self.save_folder):
            makedirs(self.save_folder)

    def _read(self):
        '''读取配置文件并返回配置内容；
        如果没有配置文件，则创建默认配置文件'''
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
            dump(self.default_settings, f, indent=4, ensure_ascii=False)
        print(f'[{GREEN}]创建默认配置文件 settings.json 成功！')

    def _load_accounts(self):
        self.accounts = deepcopy(self.settings['accounts'])
        for account in self.accounts:
            account['sec_user_id'] = self._extract_sec_user_id(account['mark'], account['url'])
            account['earliest_date'] = self._generate_date_earliest(account['earliest'])
            account['latest_date'] = self._generate_date_latest(account['latest'])
            if account['sec_user_id'] is None:
                break

    def _extract_sec_user_id(self, mark: str, url: str) -> str | None:
        sec_user_id = match(
            r'https://www\.douyin\.com/user/([A-Za-z0-9_-]+)(\?.*)?', url).group(1)
        if sec_user_id:
            return sec_user_id
        else:
            print(f'[{RED}]参数 accounts 中账号 {mark} 的 url {url} 错误，提取 sec_user_id 失败！')
            return

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

    def _load_cookies(self):
        self.cookies = deepcopy(self.settings['cookies'])
        if not isinstance(self.cookies, dict):
            print(f'[{YELLOW}]参数 "cookies" 格式错误，请重新设置！')
            self.cookies = {}
