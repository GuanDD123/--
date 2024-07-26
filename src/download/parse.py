from datetime import date

from tool import Cleaner
from config import Settings, DESCRIPTION_LENGTH


class Parse:

    def __init__(self, cleaner: Cleaner, settings: Settings) -> None:
        self.cleaner = cleaner
        self.settings = settings

    def extract_account(self, account: dict, item: dict):
        '''提取账号 id、昵称，检查账号 mark'''
        account['id'] = self.__extract_value(item, 'author.uid')
        account['name'] = self.cleaner.filter_name(
            self.__extract_value(item, 'author.nickname'),
            default='无效账号昵称')
        account['mark'] = self.cleaner.filter_name(
            account['mark'], default=account['name'])

    def extract_items(self, items: list[dict], earliest: date, latest: date):
        '''提取发布作品信息并返回'''
        results = []
        for item in items:
            result = {}
            self.__extract_common(item, result)
            if result['create_time_date'] <= latest and result['create_time_date'] >= earliest:
                if gallery := self.__extract_value(item, 'images'):
                    self.__extract_gallery(gallery, result)
                else:
                    self.__extract_video(self.__extract_value(item, 'video'), result)
                results.append(result)
        return results

    def __extract_common(self, item: dict, result: dict):
        '''提取图文/视频作品共有信息'''
        result['id'] = self.__extract_value(item, 'aweme_id')
        result['desc'] = self.cleaner.clear_spaces(self.cleaner.filter_name(
            self.__extract_value(item, 'desc')))[:DESCRIPTION_LENGTH]
        result['create_timestamp'] = self.__extract_value(item, 'create_time')
        result['create_time_date'] = date.fromtimestamp(int(result['create_timestamp']))
        result['create_time'] = date.strftime(result['create_time_date'], self.settings.date_format)

    def __extract_gallery(self, gallery: dict, result: dict):
        '''提取图文作品信息'''
        result['type'] = '图集'
        result['share_url'] = f'https://www.douyin.com/note/{result['id']}'
        result['downloads'] = ' '.join(
            self.__extract_value(image, 'url_list[0]') for image in gallery)

    def __extract_video(self, video: dict, result: dict):
        '''提取视频作品信息'''
        result['type'] = '视频'
        result['share_url'] = f'https://www.douyin.com/video/{result['id']}'
        result['downloads'] = self.__extract_value(
            video, 'play_addr.url_list[0]')
        result['uri'] = self.__extract_value(
            video, 'play_addr.uri')
        result['duration'] = self.__duration_conversion(
            self.__extract_value(video, 'duration'))
        result['height'] = self.__extract_value(video, 'height')
        result['width'] = self.__extract_value(video, 'width')
        result['ratio'] = self.__extract_value(video, 'ratio')

    @staticmethod
    def __duration_conversion(duration: int):
        '''将以 ms 为单位的时长转化为 时:分:秒 的形式'''
        return f'{
            duration // 1000 // 3600:0>2d}:{
            duration // 1000 % 3600 // 60:0>2d}:{
            duration // 1000 % 3600 % 60:0>2d}'

    @staticmethod
    def __extract_value(data: dict, attribute_chain: str):
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
