from datetime import date

from ..tool import Cleaner
from ..config import Settings, DESCRIPTION_LENGTH


class Parse:
    def __init__(self, cleaner: Cleaner, settings: Settings) -> None:
        self.cleaner = cleaner
        self.settings = settings

    def extract_account(self, account: dict, item: dict):
        '''提取账号 id、昵称，检查账号 mark'''
        account['id'] = self._extract_value(item, 'author.uid')
        account['name'] = self.cleaner.filter_name(
            self._extract_value(item, 'author.nickname'),
            default='无效账号昵称')
        account['mark'] = self.cleaner.filter_name(
            account['mark'], default=account['name'])

    def extract_items(self, items: list[dict], earliest: date, latest: date):
        '''提取发布作品信息并返回'''
        results = []
        for item in items:
            result = {}
            self._extract_common(item, result)
            if (result['create_time_date'] <= latest) and (result['create_time_date'] >= earliest):
                if (gallery := self._extract_value(item, 'images')):
                    if self.settings.download_images:
                        self._extract_gallery(gallery, result)
                        results.append(result)
                elif self.settings.download_videos:
                    self._extract_video(self._extract_value(item, 'video'), result)
                    results.append(result)
        return results

    def _extract_common(self, item: dict, result: dict):
        '''提取图文/视频作品共有信息'''
        result['id'] = self._extract_value(item, 'aweme_id')
        if desc:=self._extract_value(item, 'desc'):
            result['desc'] = self.cleaner.clear_spaces(self.cleaner.filter_name(desc))[:DESCRIPTION_LENGTH]
        else:
            result['desc'] = '作品描述为空'
        result['create_timestamp'] = self._extract_value(item, 'create_time')
        result['create_time_date'] = date.fromtimestamp(int(result['create_timestamp']))
        result['create_time'] = date.strftime(result['create_time_date'], self.settings.date_format)

    def _extract_gallery(self, gallery: dict, result: dict):
        '''提取图文作品信息'''
        result['type'] = '图集'
        result['share_url'] = f'https://www.douyin.com/note/{result["id"]}'
        result['downloads'] = []
        for image in gallery:
            url = self._extract_value(image, 'url_list[0]')
            width = self._extract_value(image, 'width')
            height = self._extract_value(image, 'height')
            result['downloads'].append((url, width, height))

    def _extract_video(self, video: dict, result: dict):
        '''提取视频作品信息'''
        result['type'] = '视频'
        result['share_url'] = f'https://www.douyin.com/video/{result["id"]}'
        result['downloads'] = self._extract_value(
            video, 'play_addr.url_list[0]')
        result['height'] = self._extract_value(video, 'height')
        result['width'] = self._extract_value(video, 'width')

    @staticmethod
    def _extract_value(data: dict, attribute_chain: str):
        '''根据 attribute_chain 从 dict 中提取值'''
        attributes = attribute_chain.split('.')
        for attribute in attributes:
            if '[' in attribute:
                parts = attribute.split('[', 1)
                attribute = parts[0]
                index = int(parts[1].split(']', 1)[0])
                data = data[attribute][index]
            else:
                data = data[attribute]
            if not data:
                return
        return data
