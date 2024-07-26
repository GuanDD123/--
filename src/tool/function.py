from config import RETRY

def retry(function):
    '''发生错误时尝试重新执行'''

    def inner(*args, **kwargs):
        if r := function(*args, **kwargs):
            return r
        else:
            for _ in range(RETRY):
                if r := function(*args, **kwargs):
                    return r
        return r

    return inner
