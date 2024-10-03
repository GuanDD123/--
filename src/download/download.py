from os import makedirs
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
from yarl import URL
from asyncio import Semaphore, gather, run, create_task, TimeoutError
from aiohttp import ClientSession, ClientResponse, ClientTimeout

from config import (
    GREEN, CYAN, YELLOW, MAGENTA,
    COOKIE_UPDATE_INTERVAL,
    CHUNK, TIMEOUT, CONCURRENCY
)
from config import Settings, Cookie
from tool import Cleaner, retry_async
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
            run(self._download_files(tasks_info, progress))

    async def _download_file(self, task_info: tuple, progress: Progress, sem: Semaphore):
        await self._request_file(*task_info, progress, sem)
        if time()-self.cookie.last_update_time >= COOKIE_UPDATE_INTERVAL:
            self.cookie.update()

    async def _download_files(self, tasks_info: list, progress: Progress):
        sem = Semaphore(CONCURRENCY)
        tasks = []
        for task_info in tasks_info:
            task = create_task(self._download_file(task_info, progress, sem))
            tasks.append(task)
        await gather(*tasks)

    def _generate_task(self, items: list[dict], save_folder: str):
        '''生成下载任务信息列表并返回'''
        tasks = []
        for item in items:
            id = item['id']
            desc = item['desc']
            name = self.cleaner.filter_name(self.settings.split.join(
                item[key] for key in self.settings.name_format))
            if (type := item['type']) == '图集':
                for index, info in enumerate(item['downloads'], start=1):
                    if (task := self._generate_task_image(id, desc, name, index, info[0], info[1], info[2], save_folder)) is not None:
                        tasks.append(task)
            elif type == '视频':
                url = item['downloads']
                width = item['width']
                height = item['height']
                if (task := self._generate_task_video(id, desc, name, url, width, height, save_folder)) is not None:
                    tasks.append(task)
        return tasks

    def _generate_task_image(self, id: str, desc: str, name: str, index: int, url: str, width: int, height: int, save_folder: str):
        '''生成图片下载任务信息'''
        show = f'图集 {id} {desc[:15]}'
        if id in self.download_recorder.records:
            print(f'[{CYAN}]{show} 存在下载记录，跳过下载')
        elif exists(path := join_path(save_folder, f'{name}_{index}.jpeg')):
            print(f'[{CYAN}]{show} 文件已存在，跳过下载')
        else:
            return (url, path, show, id, width, height)

    def _generate_task_video(self, id: str, desc: str, name: str, url: str, width: int, height: int, save_folder: str):
        '''生成视频下载任务信息'''
        show = f'视频 {id} {desc[:15]}'
        if id in self.download_recorder.records:
            print(f'[{CYAN}]{show} 存在下载记录，跳过下载')
        elif exists(path := join_path(save_folder, f'{name}.mp4')):
            print(f'[{CYAN}]{show} 文件已存在，跳过下载')
        else:
            return (url, path, show, id, width, height)

    @retry_async
    async def _request_file(self, url: str, path: str, show: str, id: str, width: int, height: int,
                            progress: Progress, sem: Semaphore):
        '''下载 url 对应文件'''
        async with sem:
            try:
                async with ClientSession(headers=self.settings.headers, timeout=ClientTimeout(TIMEOUT)) as session:
                    async with session.get(URL(url, encoded=True)) as response:
                        if not (content_length := int(response.headers.get('content-length', 0))):
                            print(f'[{YELLOW}]{show} {url} 响应内容为空')
                        elif response.status != 200 and response.status != 206:
                            print(f'[{YELLOW}]{show} {url} 响应状态码异常 {response.status}')
                        else:
                            await self._save_file(path, show, id, width, height, response, content_length, progress)
                            return True
            except TimeoutError:
                print(f'[{YELLOW}]{show} {url} 响应超时')

    async def _save_file(self, path: str, show: str, id: str, width: int, height: int,
                         response: ClientResponse, content_length: int, progress: Progress):
        task_id = progress.add_task(show, total=content_length or None)
        with open(path, 'wb') as f:
            async for chunk in response.content.iter_chunked(CHUNK):
                f.write(chunk)
                progress.update(task_id, advance=len(chunk))
        progress.remove_task(task_id)
        if max(width, height) < 1920:
            color = YELLOW
        else:
            color = GREEN
        print(f'[{GREEN}]{show} [{color}]清晰度：{width}×{height} [{GREEN}]下载成功')
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
