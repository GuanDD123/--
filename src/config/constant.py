from os.path import dirname
from os import name

PROJECT_ROOT = dirname(dirname(dirname(__file__)))

ENCODE = 'UTF-8-SIG' if name == 'nt' else 'UTF-8'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
PHONE_USER_AGENT = 'com.ss.android.ugc.trill/494+Mozilla/5.0+(Linux;+Android+12;+2112123G+Build/SKQ1.211006.001;+wv)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Version/4.0+Chrome/107.0.5304.105+Mobile+Safari/537.36'

# 颜色设置，支持标准颜色名称、Hex、RGB 格式
WHITE = '#aaaaaa'
CYAN = 'bright_cyan'
RED = 'bright_red'
YELLOW = 'bright_yellow'
GREEN = 'bright_green'
MAGENTA = 'bright_magenta'

# 文件 desc 最大长度限制
DESCRIPTION_LENGTH = 64

# 重新执行的最大次数
RETRY_ACCOUNT = 3
RETRY_FILE = 2

# 非法字符集合
TEXT_REPLACEMENT = frozenset()

# 每次从服务器接收的数据块大小
CHUNK = 1024 * 1024

# 请求超时时间
TIMEOUT = 60 * 5

# 文件下载最大协程数
CONCURRENCY = 5
