from os.path import (
    join as join_path,
    exists,
)
from os import makedirs
from shutil import rmtree
from threading import Event
from threading import Thread
from contextlib import suppress
from datetime import date

from config import (
    PROJECT_ROOT,
    COOKIE_UPDATE_INTERVAL,
    TEXT_REPLACEMENT,
    INFO, WARNING
)
from config import Settings, Cookie
from tool import ColorfulConsole, Cleaner
from download import Acquire, Download, Parse
from backup import DownloadRecorder, DownloadItems


class Scheduler:

    def __init__(self) -> None:
        self.console = ColorfulConsole()
        self.download_recorder = DownloadRecorder(self.console)
        self.download_items = DownloadItems(self.console)
        self.cleaner = Cleaner(self.console)
        self.settings = Settings(self.console)
        self.cookie = Cookie(self.settings, self.console)
        self.parse = Parse(self.cleaner, self.settings)
        self.download = Download(self.console, self.settings, self.cleaner, self.download_recorder)
        self.acquirer = Acquire(self.settings, self.console)
        self.event = Event()
        self.cookie_task = Thread(target=self.periodic_update_cookie)
        self.running = True

    def periodic_update_cookie(self):
        while not self.event.is_set():
            self.cookie.update()
            self.event.wait(COOKIE_UPDATE_INTERVAL)

    def run(self):
        self.check_config()
        self.main_menu()
        self.close()

    def check_config(self):
        self.cleaner.set_rule(TEXT_REPLACEMENT)
        cache_folder = join_path(PROJECT_ROOT, 'cache')
        self.running = self.settings.check()
        if exists(cache_folder):
            account, items = self.download_items.read()
            if account and items:
                self.download_recorder.read()
                self.console.print('开始提取上次未下载完作品数据', style=INFO)
                account_id = account['id']
                account_mark = account['mark']
                self.console.print(
                    f'账号标识：{account_mark}；账号 ID：{account_id}',
                    style=INFO)
                self.download_recorder.open_()
                self.download.download_files(items, account_id, account_mark)
                self.download_recorder.f_obj.close()
        else:
            makedirs(cache_folder)

    def main_menu(self):
        if not self.cookie_task.is_alive():
            self.cookie_task.start()
        self.__function = (
            ('复制粘贴写入 Cookie', self.write_cookie),
            ('从浏览器获取 Cookie', self.cookie.browser_save),
            ('批量下载账号作品(配置文件)', self.account_acquisition_interactive,)
        )
        while self.running:
            with suppress(ValueError):
                mode = self.choose(
                    title='请选择 TikTokDownloader 运行模式',
                    options=[option for option, _ in self.__function],
                    separate_lines=(2, 3))
                if mode in ('Q', 'q', ''):
                    self.running = False
                elif not mode:
                    continue
                else:
                    index = int(mode) - 1
                    if index < len(self.__function) and index >= 0:
                        self.__function[index][1]()
            mode = None

    def account_acquisition_interactive(self):
        accounts = self.settings.accounts
        self.console.print(f'共有 {len(accounts)} 个账号的作品等待下载', style=INFO)
        for num, account in enumerate(accounts, start=1):
            if not self.deal_account_works(num, account):
                if num != len(accounts):
                    continue

    def deal_account_works(self, num: int, account: dict[str, str | date]):
        self.console.print(f'\n\n开始处理第 {num} 个账号' if num else '开始处理账号')
        self.console.print(f'最早发布日期：{account['earliest'] or '空'}，最晚发布日期：{account['latest'] or '空'}')
        items = self.acquirer.request_items(account['sec_user_id'], account['earliest_date'])
        if not any(items):
            self.console.print('获取账号主页数据失败', style=WARNING)
            return False
        else:
            self.console.print('开始提取作品数据', style=INFO)
            self.parse.extract_account(account, items[0])
            account_id = account['id']
            account_mark = account['mark']
            self.console.print(
                f'账号标识：{account_mark}；账号 ID：{account_id}',
                style=INFO)
            items = self.parse.extract_items(items, account['earliest_date'], account['latest_date'])
            self.download_items.save(account, items)
            self.download_recorder.open_()
            self.download.download_files(items, account_id, account_mark)
            self.download_recorder.f_obj.close()
            return True

    def write_cookie(self):
        self.cookie.input_save()
        self.cookie.update()

    def choose(self, title: str, options: list[str], separate_lines: tuple[int] = None):
        '''返回选择的运行模式编号'''
        tips = f'{title}:\n'
        for line_num, option in enumerate(options, start=1):
            tips += f'{line_num: >2d}. {option}\n'
            if separate_lines and (line_num in separate_lines):
                tips += f'{'=' * 25}\n'
        return self.console.input(tips)

    def close(self):
        rmtree(join_path(PROJECT_ROOT, 'cache'))
        self.event.set()
        self.download_recorder.delete()
        self.download_items.delete()
        self.console.print('程序结束运行')
