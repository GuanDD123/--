from re import finditer
from rich import print

from .constant import CYAN, GREEN
from .settings import Settings
from ..encrypt_params import MsToken, TtWid


class Cookie:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def input_save(self):
        '''输入 cookie，转为 dict，保存到 Settings.cookies 属性中，并存入配置文件'''
        while not (cookie := input(f'请粘贴 Cookie 内容: ')):
            continue
        self.settings.cookies = self._generate_dict(cookie)
        self._check()
        self._save()

    def update(self):
        '''更新 Settings.cookies 与 Settings.headers'''
        if self.settings.cookies:
            self._add_cookies()
            self.settings.headers['Cookie'] = self._generate_str(self.settings.cookies)

    def _check(self):
        '''检查 Settings.cookies 是否已登录；删除空键值对'''
        if not self.settings.cookies['sessionid_ss']:
            print(f'[{CYAN}]当前 Cookie 未登录')
        else:
            print(f'[{CYAN}]当前 Cookie 已登录')

        keys_to_remove = [key for key, value in self.settings.cookies.items() if value is None]
        for key in keys_to_remove:
            del self.settings.cookies[key]

    def _save(self):
        '''将 Settings.cookies 存储到 settings.json'''
        self.settings.settings['cookies'] = self.settings.cookies
        self.settings.save()
        print(f'[{GREEN}]写入 Cookie 成功！')

    def _add_cookies(self):
        parameters = (MsToken.get_real_ms_token(), TtWid.get_tt_wid())
        for i in parameters:
            if isinstance(i, dict):
                self.settings.cookies |= i

    @staticmethod
    def _generate_str(cookies: dict):
        '''根据 dict 生成 str'''
        if cookies:
            result = [f'{k}={v}' for k, v in cookies.items()]
            return '; '.join(result)

    @staticmethod
    def _generate_dict(cookie: str):
        '''根据 str 生成 dict'''
        cookies_key = {
            'passport_csrf_token',
            'passport_csrf_token_default',
            'my_rd',
            'passport_auth_status',
            'passport_auth_status_ss',
            'd_ticket',
            'publish_badge_show_info',
            'volume_info',
            '__live_version__',
            'download_guide',
            'EnhanceDownloadGuide',
            'pwa2',
            'live_can_add_dy_2_desktop',
            'live_use_vvc',
            'store-region',
            'store-region-src',
            'strategyABtestKey',
            'FORCE_LOGIN',
            'LOGIN_STATUS',
            '__security_server_data_status',
            '_bd_ticket_crypt_doamin',
            'n_mh',
            'passport_assist_user',
            'sid_ucp_sso_v1',
            'ssid_ucp_sso_v1',
            'sso_uid_tt',
            'sso_uid_tt_ss',
            'toutiao_sso_user',
            'toutiao_sso_user_ss',
            'sessionid',
            'sessionid_ss',
            'sid_guard',
            'sid_tt',
            'sid_ucp_v1',
            'ssid_ucp_v1',
            'uid_tt',
            'uid_tt_ss',
            'FOLLOW_NUMBER_YELLOW_POINT_INFO',
            'vdg_s',
            '_bd_ticket_crypt_cookie',
            'FOLLOW_LIVE_POINT_INFO',
            'bd_ticket_guard_client_data',
            'bd_ticket_guard_client_web_domain',
            'home_can_add_dy_2_desktop',
            'odin_tt',
            'stream_recommend_feed_params',
            'IsDouyinActive',
            'stream_player_status_params',
            's_v_web_id',
            '__ac_nonce',
            'dy_sheight',
            'dy_swidth',
            'ttcid',
            'xgplayer_user_id',
            '__ac_signature',
            'tt_scid'
        }
        cookies = {}.fromkeys(cookies_key)
        matches = finditer(r'(?P<key>[^=;,]+)=(?P<value>[^;,]+)', cookie)
        for match in matches:
            key = match.group('key').strip()
            value = match.group('value').strip()
            if key in cookies_key:
                cookies[key] = value
        return cookies
