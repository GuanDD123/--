from rich.console import Console

from config import GENERAL, PROMPT


class ColorfulConsole(Console):

    def print(self, *args, style=GENERAL, highlight=False, **kwargs):
        super().print(*args, style=style, highlight=highlight, **kwargs)

    def input(self, prompt_='', style=PROMPT, *args, **kwargs):
        return super().input(f'[{style}]{prompt_}[/{style}]', *args, **kwargs)
