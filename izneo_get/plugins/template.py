from .site_processor import SiteProcessor
import re
from ..book_infos import BookInfos
from ..config import Config


class Template(SiteProcessor):
    URL_PATTERNS = ["https://www.template.com/.*"]

    def __init__(self, url: str = ""):
        super().__init__(url)

    def authenticate() -> None:
        ...

    def download(self):
        ...

    def get_book_infos(self) -> BookInfos:
        ...


def init(url: str = "", config: Config = None) -> Template:
    return Template(url, config)
