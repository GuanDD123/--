from os.path import (
    join as join_path,
    exists,
)
from os import makedirs
from shutil import rmtree
from datetime import date
from rich import print
from time import time
import subprocess

from .config import (
    PROJECT_ROOT,
    COOKIE_UPDATE_INTERVAL,
    TEXT_REPLACEMENT,
    WHITE, CYAN
)
from .config import Settings, Cookie
from .tool import Cleaner
from .download import Acquire, Download, Parse
from .backup import DownloadRecorder, DownloadItems


class Scheduler:
    def __init__(self) -> None:
        self.download_recorder = DownloadRecorder()
        self.download_items = DownloadItems()
        self.cleaner = Cleaner()
        self.settings = Settings()
        self.cookie = Cookie(self.settings)
        self.parse = Parse(self.cleaner, self.settings)
        self.download = Download(self.settings, self.cleaner, self.cookie, self.download_recorder)
        self.acquirer = Acquire(self.settings)

    def run(self):
        self.check_config()
        self.main_menu()
        self.close()

    def check_config(self):
        self.cleaner.set_rule(TEXT_REPLACEMENT)
        self.cache_folder = join_path(PROJECT_ROOT, 'cache')
        self.settings.check()

    def main_menu(self):
        self.cookie.update()
        for i in (
            '='*25,
            '1. 复制粘贴写入 Cookie',
            '2. 修改配置文件(Linux)',
            '='*25,
            '3. 批量下载账号作品(配置文件)',
            '='*25,
        ):
            print(f'[{CYAN}]{i}')
        while (mode := input('\n请选择运行模式：').strip()).lower() != 'q':
            if mode == '1':
                self.cookie.input_save()
            elif mode == '2':
                subprocess.run(['xdg-open', self.settings.file])
                try:
                    subprocess.run(['xdg-open', join_path(PROJECT_ROOT, '已下载账号信息.json')])
                except:
                    pass
                input()
                self.settings.check()
            elif mode == '3':
                if exists(self.cache_folder):
                    self._continue_last_download()
                else:
                    makedirs(self.cache_folder)
                self._deal_accounts()

    def close(self):
        try:
            rmtree(self.cache_folder)
            self.download_recorder.delete()
            self.download_items.delete()
        finally:
            print(f'[{WHITE}]程序结束运行')

    def _continue_last_download(self):
        if input('检测到程序上次未正常退出，是否提取上次下载信息：').lower() == 'y':
            account, items = self.download_items.read()
            if account and items:
                self.cookie.update()
                self.download_recorder.read()
                print(f'[{CYAN}]\n开始提取上次未下载完作品数据')
                account_id = account['id']
                account_mark = account['mark']
                print(f'[{CYAN}]账号标识：{account_mark}；账号 ID：{account_id}')
                self.download_recorder.open_()
                self.download.download_files(items, account_id, account_mark)
                self.download_recorder.f_obj.close()
        else:
            self.download_recorder.delete()
            self.download_items.delete()

    def _deal_accounts(self):
        accounts = self.settings.accounts
        print(f'[{CYAN}]共有 {len(accounts)} 个账号的作品等待下载')
        for num, account in enumerate(accounts, start=1):
            self._deal_account(num, account)
            if time()-self.cookie.last_update_time >= COOKIE_UPDATE_INTERVAL:
                self.cookie.update()

    def _deal_account(self, num: int, account: dict[str, str | date]):
        for i in (
            f'\n开始处理第 {num} 个账号' if num else '开始处理账号',
            f'账号标识：{account["mark"] or "空"}',
            f'最早发布日期：{account["earliest"] or "空"}，最晚发布日期：{account["latest"] or "空"}'
        ):
            print(f'[{CYAN}]{i}')
        items = self.acquirer.request_items(account['sec_user_id'], account['earliest_date'])
        if items:
            print(f'[{CYAN}]\n开始提取作品数据')
            self.parse.extract_account(account, items[0])
            account_id = account['id']
            account_mark = account['mark']
            print(f'[{CYAN}]账号标识：{account_mark}；账号 ID：{account_id}')
            items = self.parse.extract_items(items, account['earliest_date'], account['latest_date'])
            print(f'[{CYAN}]当前账号作品数量: {len(items)}')
            self.download_items.save(account, items)
            self.download_recorder.open_()
            self.download.download_files(items, account_id, account_mark)
            self.download_recorder.f_obj.close()
            return True
