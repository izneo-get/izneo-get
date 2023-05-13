from typing import Optional
from .site_processor import SiteProcessor
from ..book_infos import BookInfos
from ..config import Config


class Template(SiteProcessor):
    URL_PATTERNS = ["https://www.template.com/.*"]
    url: str
    config: Config
    cache_file: str

    def __init__(self, url: str = "", config: Optional[Config] = None):
        super().__init__(url, config)

    def authenticate(self) -> None:
        ...

    def download(self, forced_title: Optional[str] = None) -> str:
        ...

    def get_book_infos(self) -> BookInfos:
        ...


def init(url: str = "", config: Optional[Config] = None) -> Template:
    return Template(url, config)
