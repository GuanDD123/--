from time import time
from random import random

class VerifyFp:
    '''代码参考: https://github.com/Johnserf-Seed/TikTokDownload/blob/main/Util/Cookies.py'''

    @staticmethod
    def get_verify_fp():
        e = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        t = len(e)
        milliseconds = int(round(time() * 1000))
        base36 = ''
        while milliseconds > 0:
            remainder = milliseconds % 36
            if remainder < 10:
                base36 = str(remainder) + base36
            else:
                base36 = chr(ord('a') + remainder - 10) + base36
            milliseconds //= 36
        r = base36
        o = [''] * 36
        o[8] = o[13] = o[18] = o[23] = '_'
        o[14] = '4'

        for i in range(36):
            if not o[i]:
                n = 0 or int(random() * t)
                if i == 19:
                    n = 3 & n | 8
                o[i] = e[n]
        return f'verify_{r}_' + ''.join(o)
