from os import makedirs, remove
from os.path import join as join_path, exists
from rich.progress import (
    SpinnerColumn,
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)
from rich import print
from time import time
from requests import get, exceptions, Response

from config import (
    GREEN, CYAN, YELLOW, MAGENTA,
    COOKIE_UPDATE_INTERVAL
)
from config import Settings, Cookie
from tool import retry, Cleaner
from backup import DownloadRecorder


class Download:

    def __init__(self, settings: Settings, cleaner: Cleaner, cookie: Cookie,
                 download_recorder: DownloadRecorder):
        self.download_recorder = download_recorder
        self.settings = settings
        self.cleaner = cleaner
        self.cookie = cookie

    def download_files(self, items: list[dict], account_id: str, account_mark: str):
        '''下载作品文件'''
        print(f'[{CYAN}]\n开始下载作品文件\n')
        save_folder = self._create_save_folder(account_id, account_mark)
        tasks_info = self._generate_task(items, save_folder)
        with self._progress_object() as progress:
            for task_info in tasks_info:
                self._request_file(*task_info, progress=progress)
                if time()-self.cookie.last_update_time >= COOKIE_UPDATE_INTERVAL:
                    self.cookie.update()

    def _generate_task(self, items: list[dict], save_folder: str):
        '''生成下载任务信息列表并返回'''
        tasks = []
        for item in items:
            id = item['id']
            name = self.cleaner.filter_name(self.settings.split.join(
                item[key] for key in self.settings.name_format))
            if (type := item['type']) == '图集':
                for index, url in enumerate(item['downloads'].split(' '), start=1):
                    if (task := self._generate_task_image(id, name, index, url, save_folder)) is not None:
                        tasks.append(task)
            elif type == '视频':
                if (task := self._generate_task_video(id, name, item, save_folder)) is not None:
                    tasks.append(task)
        return tasks

    def _generate_task_image(self, id: str, name: str, index: int, url: str, save_folder: str):
        '''生成图片下载任务信息'''
        if id in self.download_recorder.records:
            print(f'[{CYAN}]{name} 存在下载记录，跳过下载')
        elif exists(path := join_path(save_folder, f'{name}_{index}.jpeg')):
            print(f'[{CYAN}]{name} 文件已存在，跳过下载')
        else:
            return (url, path, name, id)

    def _generate_task_video(self, id: str, name: str, video: dict, save_folder: str):
        '''生成视频下载任务信息'''
        if (id in self.download_recorder.records) or exists(path := join_path(save_folder, f'{name}.mp4')):
            print(f'[{CYAN}]{name} 存在下载记录或文件已存在，跳过下载')
        else:
            return (video['downloads'], path, name, id)

    @retry
    def _request_file(self, url: str, path: str, name: str, id: str, progress: Progress):
            '''下载 url 对应文件'''
            try:
                with get(url, stream=True, headers=self.settings.headers, timeout=self.settings.timeout) as response:
                    if not (content_length := int(response.headers.get('content-length', 0))):
                        print(f'[{YELLOW}]{name} {url} 响应内容为空')
                    elif response.status_code != 200 and response.status_code != 206:
                        print(f'[{YELLOW}]{name} {response.url} 响应码异常: {response.status_code}')
                    else:
                        self._save_file(path, name, id, response, content_length, progress)
                        return True
            except (exceptions.ConnectionError, exceptions.ChunkedEncodingError, exceptions.ReadTimeout) as e:
                print(f'[{YELLOW}]{name} 网络异常: {e}')

    def _save_file(self, path: str, name: str, id: str, response: Response, content_length: int, progress: Progress):
        task_id = progress.add_task(name, total=content_length or None)
        try:
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.settings.chunk):
                    f.write(chunk)
                    progress.update(task_id, advance=len(chunk))
                progress.remove_task(task_id)
        except exceptions.ChunkedEncodingError:
            progress.remove_task(task_id)
            print(f'[{YELLOW}]{name} 由于网络异常下载中断')
            remove(path)
        else:
            print(f'[{GREEN}]{name} 文件下载成功')
            self.download_recorder.save(id)

    def _progress_object(self):
        return Progress(
            TextColumn('[progress.description]{task.description}', style=MAGENTA, justify='left'),
            SpinnerColumn(),
            BarColumn(bar_width=20),
            '[progress.percentage]{task.percentage:>3.1f}%',
            '•',
            DownloadColumn(binary_units=True),
            '•',
            TimeRemainingColumn(),
            transient=True,
        )

    def _create_save_folder(self, id: str, mark: str):
        '''新建存储文件夹，返回文件夹路径'''
        folder = join_path(self.settings.save_folder, f'UID{id}_{mark}_发布作品')
        makedirs(folder, exist_ok=True)
        return folder
