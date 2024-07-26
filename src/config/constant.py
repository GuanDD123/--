from os.path import dirname
from os import name

PROJECT_ROOT = dirname(dirname(dirname(__file__)))

ENCODE = 'UTF-8-SIG' if name == 'nt' else 'UTF-8'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
PHONE_USER_AGENT = 'com.ss.android.ugc.trill/494+Mozilla/5.0+(Linux;+Android+12;+2112123G+Build/SKQ1.211006.001;+wv)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Version/4.0+Chrome/107.0.5304.105+Mobile+Safari/537.36'

# 彩色交互提示颜色设置，支持标准颜色名称、Hex、RGB 格式
MASTER = 'b yellow'
PROMPT = 'b bright_cyan'
PROGRESS = 'b bright_magenta'
GENERAL = 'b bright_white'
ERROR = 'b bright_red'
WARNING = 'b bright_yellow'
INFO = 'b bright_green'

# 文件 desc 最大长度限制
DESCRIPTION_LENGTH = 64

# 重新执行的最大次数
RETRY = 5

# 协程最大数量
MAX_WORKERS = 5

# Cookie 更新间隔，单位：秒
COOKIE_UPDATE_INTERVAL = 10 * 60

# 非法字符集合
TEXT_REPLACEMENT = frozenset({})
