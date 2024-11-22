from os.path import (
    join as join_path,
    exists,
)
from os import remove
from rich import print

from ..config import (
    YELLOW,
    PROJECT_ROOT,
    ENCODE
)


class DownloadRecorder:
    path = join_path(PROJECT_ROOT, 'cache/IDRecorder.txt')

    def __init__(self):
        self.records = set()

    def read(self):
        '''获取下载记录，保存到 self.records'''
        if exists(self.path):
            with open(self.path, encoding=ENCODE) as f:
                self.records = {line.strip() for line in f}
        else:
            print(f'[{YELLOW}]作品下载记录数据已丢失！\n数据文件路径：{self.path}')

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