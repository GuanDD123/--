try:
    from sys import path
    from os.path import dirname, join
    path.append(join(dirname(__file__), 'src'))
except:
    print('src 模块路径导入失败！！')
    quit()

from src.scheduler import Scheduler

if __name__ == '__main__':
    Scheduler().run()
