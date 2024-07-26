from random import randint
from string import ascii_letters, digits
from json import dumps
from time import time


from .general import send_post, extract_value
from .general import HEADERS


class MsToken:
    '''代码参考: https://github.com/Johnserf-Seed/f2/blob/main/f2/apps/douyin/utils.py'''

    @staticmethod
    def get_fake_ms_token(key='msToken', size=107):
        '''根据传入长度产生随机字符串'''
        base_str = ascii_letters + digits
        length = len(base_str) - 1
        return {key: ''.join(
            base_str[randint(0, length)] for _ in range(size))}

    @staticmethod
    def get_real_ms_token():
        headers = HEADERS | {'Content-Type': 'text/plain;charset=UTF-8'}
        api = 'https://mssdk.bytedance.com/web/report'
        data = {
            'magic': 538969122,
            'version': 1,
            'dataType': 8,
            'strData': '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',
        }
        if response := send_post(api, headers,
                             dumps(data | {'tspFromClient': int(time() * 1000)})):
            return extract_value(response.headers, 'msToken')
