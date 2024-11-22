from platform import system
from string import whitespace
from rich import print

from ..config import YELLOW


class Cleaner:

    def __init__(self):
        '''替换字符串中包含的非法字符，
        默认根据系统类型生成对应的非法字符集合，也可以自行设置非法字符集合'''
        self.rule = self.default_rule()

    def default_rule(self):
        '''根据系统类型生成默认非法字符集合'''
        now_system = system()
        if now_system in ('Windows', 'Darwin'):
            rule = {'/', '\\', '|', '<', '>', '\'', '\"', '?', ':', '*', '\x00'}  # Windows 系统和 Mac 系统
        elif now_system == 'Linux':
            rule = {'/', '\x00'}  # Linux 系统
        else:
            print(f'[{YELLOW}]不受支持的操作系统类型，可能无法正常去除非法字符！')
            rule = set()
        return rule | {i for i in whitespace[1:]}  # 补充换行符等非法字符

    def set_rule(self, rule: set, update=True):
        '''设置非法字符集合
        update: 如果是 True，则与原有规则集合合并，否则替换原有规则集合'''
        self.rule = self.rule | rule if update else rule

    def filter_name(self, text: str, inquire=False, default: str = ''):
        '''去除非法字符'''
        for i in self.rule:
            text = text.replace(i, ' ')
        text = text.strip().strip('.')

        if inquire:
            return text or self.filter_name(self.illegal_nickname())
        else:
            return text or default

    @staticmethod
    def clear_spaces(string: str):
        '''将连续的空格转换为单个空格'''
        return ' '.join(string.split())

    def illegal_nickname(self):
        '''当 账号昵称/标识 过滤非法字符后不是有效的文件夹名称时，如何处理异常'''
        return input('当前 账号昵称/标识 不是有效的文件夹名称，请输入临时的账号标识或者合集标识：')
