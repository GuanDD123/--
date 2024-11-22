from os.path import (
    join as join_path,
    exists
)
from os import remove
from json import dump, load
from rich import print

from ..config import (
    PROJECT_ROOT,
    ENCODE,
    YELLOW
)


class DownloadItems:
    path = join_path(PROJECT_ROOT, 'cache/ItemsInfo.json')

    def read(self):
        '''获取账号信息、作品信息并返回'''
        if exists(self.path):
            with open(self.path, encoding=ENCODE) as f:
                data = load(f)
                return (data[0], data[1:])
        else:
            print(f'[{YELLOW}]账号信息、作品信息数据已丢失！\n数据文件路径：{self.path}')
            return (None, None)

    def save(self, account: dict, items: list[dict]):
        '''将账号信息及作品信息覆写到文件'''
        with open(self.path, 'w', encoding=ENCODE) as f:
            data = []
            data.append(account)
            data.extend(items)
            dump(data, f, ensure_ascii=False, indent=4, default=lambda x: str(x))

    def delete(self):
        '''删除账号信息、作品信息信息文件'''
        if exists(self.path):
            remove(self.path)
