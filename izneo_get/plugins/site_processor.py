import re
from typing import List
from ..config import Config
from ..book_infos import BookInfos


class SiteProcessor:
    URL_PATTERNS: List[str] = []
    url: str = ""
    config: Config

    def __init__(self, url: str = "", config: Config = None) -> None:
        self.url = url
        self.config = config or Config()

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return any(re.match(pattern, url) is not None for pattern in SiteProcessor.URL_PATTERNS)

    def authenticate() -> None:
        ...

    def download(self) -> str:
        ...

    def get_book_infos(self) -> BookInfos:
        ...


def init(url: str = "", config: Config = None) -> SiteProcessor:
    return SiteProcessor(url, config)
