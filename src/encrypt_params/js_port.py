from os.path import join as join_path
from urllib import parse
from py_mini_racer import MiniRacer

from ..config import PROJECT_ROOT, USER_AGENT

def get_a_bogus(query: dict):
    path = join_path(PROJECT_ROOT, 'src/encrypt_params/a_bogus.js')
    with open(path, 'r', encoding='utf-8') as f:
        a_bogus_js_code = f.read()
    a_bogus_ctx = MiniRacer()
    a_bogus_ctx.eval(a_bogus_js_code)
    query = parse.unquote(parse.urlencode(query))
    a_bogus = a_bogus_ctx.call('generate_a_bogus', query, USER_AGENT)
    return a_bogus
