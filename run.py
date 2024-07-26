try:
    import sys
    sys.path.append('./src')
except:
    print('src 模块路径导入失败！！')
    quit()

from src.scheduler import Scheduler

if __name__ == '__main__':
    Scheduler().run()
