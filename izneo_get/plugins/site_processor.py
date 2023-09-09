# -*- coding: utf-8 -*-
import os
import re
from typing import List, Optional
from ..config import Config
from ..book_infos import BookInfos
from ..tools import clean_name, get_name_from_pattern


class SiteProcessor:
    URL_PATTERNS: List[str] = []
    url: str = ""
    config: Config
    cache_file: str

    def __init__(self, url: str = "", config: Optional[Config] = None) -> None:
        self.url = url
        self.config = config or Config()

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return any(re.match(pattern, url) is not None for pattern in SiteProcessor.URL_PATTERNS)

    def authenticate(self) -> None:
        ...

    def download(self, forced_title: Optional[str] = None) -> str:
        ...

    def get_book_infos(self) -> BookInfos:
        ...

    def create_output_folder(self, book_infos: BookInfos, output_folder: Optional[str]) -> str:
        if not output_folder:
            output_folder = "DOWNLOADS"
        output_folder = get_name_from_pattern(output_folder, book_infos)
        output_folder = clean_name(output_folder, directory=True)
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def get_default_title(self, book_infos: BookInfos) -> str:
        title_used = book_infos.title
        subtitle = book_infos.subtitle or ""
        volume = book_infos.volume or ""
        if len(subtitle) > 0:
            title_used = f"{book_infos.title} - {subtitle}"
            if len(volume) > 0:
                title_used = f'{book_infos.title} - {f"00000{volume}"[-max(2, len(volume)):]}. {subtitle}'
        if len(subtitle) == 0 and len(volume) > 0:
            title_used = f'{book_infos.title} - {f"00000{volume}"[-max(2, len(volume)):]}'
        return title_used


def init(url: str = "", config: Optional[Config] = None) -> SiteProcessor:
    return SiteProcessor(url, config)
