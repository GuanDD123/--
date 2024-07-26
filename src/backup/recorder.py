from os.path import (
    join as join_path,
    exists,
)
from os import remove

from config import (
    WARNING,
    PROJECT_ROOT,
    ENCODE
)
from tool import ColorfulConsole


class DownloadRecorder:
    path = join_path(PROJECT_ROOT, 'cache/IDRecorder.txt')

    def __init__(self, console: ColorfulConsole):
        self.console = console
        self.records = set()

    def read(self):
        '''获取下载记录，保存到 self.records'''
        if exists(self.path):
            with open(self.path, encoding=ENCODE) as f:
                self.records = {line.strip() for line in f}
        else:
            self.console.print(
                f'作品下载记录数据已丢失！\n数据文件路径：{self.path}',
                style=WARNING)

    def open_(self):
        self.f_obj = open(self.path, 'a', encoding=ENCODE)

    def save(self, id: str):
        '''将已下载 id 添加到文件'''
        self.f_obj.write(f'{id}\n')
        self.f_obj.flush()

    def delete(self):
        '''删除下载记录文件'''
        if exists(self.path):
            remove(self.path)