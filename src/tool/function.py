from ..config import RETRY_ACCOUNT, RETRY_FILE

def retry(function):
    '''发生错误时尝试重新执行'''

    def inner(*args, **kwargs):
        if r := function(*args, **kwargs):
            return r
        else:
            for _ in range(RETRY_ACCOUNT):
                if r := function(*args, **kwargs):
                    return r
        return r

    return inner

def retry_async(function):
    '''发生错误时尝试重新执行'''

    async def inner(*args, **kwargs):
        if r := await function(*args, **kwargs):
            return r
        else:
            for _ in range(RETRY_FILE):
                if r := await function(*args, **kwargs):
                    return r
        return r

    return inner
