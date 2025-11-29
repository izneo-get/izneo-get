# -*- coding: utf-8 -*-
import asyncio
import os
import re
from typing import Dict, List, Optional

import requests
from tqdm.asyncio import tqdm

from ..book_infos import BookInfos
from ..config import Config, ImageFormat, OutputFormat
from ..tools import (
    BAR_FORMAT,
    async_http_get,
    clean_name,
    get_image_type,
    get_name_from_pattern,
)


class SiteProcessor:
    URL_PATTERNS: List[str] = []
    url: str = ""
    config: Config
    cache_file: str
    session: Optional[requests.Session] = None
    headers: Dict[str, str] = {}

    def __init__(self, url: str = "", config: Optional[Config] = None) -> None:
        self.url = url
        self.config = config or Config()
        if self.config.user_agent:
            self.headers = {"User-Agent": self.config.user_agent}

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return any(
            re.match(pattern, url) is not None for pattern in SiteProcessor.URL_PATTERNS
        )

    def authenticate(self) -> None: ...

    def get_book_infos(self) -> BookInfos: ...

    def download(self, forced_title: Optional[str] = None) -> str:
        print(f"URL: {self.url}")
        self.before_download()
        book_infos = self.get_book_infos()

        # Si on n'a pas les informations de base, on arrête tout de suite.
        if not book_infos.title or not book_infos.pages:
            print("ERROR: Can't find book.")
            self.after_download([])
            return ""

        # Création du répertoire de destination.
        output_folder = self.create_output_folder(book_infos, self.config.output_folder)

        title_used = self._get_title_to_use(book_infos)

        if forced_title:
            forced_title = get_name_from_pattern(forced_title, book_infos)
            print(
                f'Download "{clean_name(title_used)}" as "{clean_name(forced_title)}"'
            )
            title_used = forced_title
        else:
            print(f'Download "{clean_name(title_used)}"')
        title_used = clean_name(title_used)
        save_path = f"{output_folder}/{title_used}"

        print(f"{book_infos.pages} pages expected")

        # Si l'archive existe déjà, on ne télécharge pas cette BD.
        if (
            self.config.continue_from_existing
            and self.config.output_format == OutputFormat.CBZ
            and os.path.exists(f"{save_path}.cbz")
        ):
            print(f'"{save_path}.cbz" already exists, skipping.')
            self.after_download([])
            return ""
        self._create_destination_folder(save_path)

        files_downloaded: List[str] = []
        if self.config.pause_sec:
            files_downloaded = self._download_all_pages(title_used, save_path)
        else:
            files_downloaded = asyncio.run(
                self._async_download_all_pages(title_used, save_path)
            )
        count_empty = len([element for element in files_downloaded if not element])
        print(f"{len(files_downloaded) - count_empty} pages downloaded")
        if count_empty:
            print(f"{count_empty} pages skipped")
        self.after_download(files_downloaded)
        return save_path

    def before_download(self) -> None: ...

    def after_download(self, files_downloaded: List[str]) -> None: ...

    def post_process_image_content(
        self, response: requests.models.Response, page_num: int = 0
    ) -> bytes:
        return response.content

    async def _async_download_page(
        self,
        page_num: int,
        url: str,
        title_used: str,
        save_path: str,
        pause_sec: int = 0,
    ) -> str:
        book_infos = self.get_book_infos()
        if len(book_infos.page_urls) == 0:
            print("ERROR: Can't find pages in book infos.")
            return ""

        nb_digits = max(3, len(str(book_infos.pages)))

        # Si la page existe déjà sur le disque, on passe.
        page_txt = f"000000000{str(page_num + 1)}"[-nb_digits:]
        store_path = f"{save_path}/{title_used} {page_txt}.tmp"
        store_path_converted = ""
        if self.config.image_format == ImageFormat.WEBP:
            store_path_converted = f"{save_path}/{title_used} {page_txt}.webp"
        if self.config.image_format == ImageFormat.JPEG:
            store_path_converted = f"{save_path}/{title_used} {page_txt}.jpeg"
        if (
            self.config.continue_from_existing
            and self.config.image_format in {ImageFormat.JPEG, ImageFormat.WEBP}
            and os.path.exists(store_path_converted)
            and os.path.getsize(store_path_converted)
        ):
            return store_path_converted

        # r = s.get(url, cookies=s.cookies, allow_redirects=True, params=params, headers=headers)
        try:
            r = await async_http_get(url, session=self.session, headers=self.headers)
        except requests.TooManyRedirects as e:
            print(f"\n[ERROR] Page {page_num} unavailable: {e}")
            return ""

        if r.status_code in (403, 404):
            if page_num < book_infos.pages:
                print(
                    f"\n[ERROR] Can't download page {str(page_num + 1)} ({str(book_infos.pages)} pages expected)"
                )
            return ""
        if r.encoding:
            print(f"\n[ERROR] Page {page_num} unavailable")
            return ""

        # Decode image.
        uncrypted = self.post_process_image_content(r, page_num=page_num)
        store_path = f"{save_path}/{title_used} {page_txt}.tmp"
        open(store_path, "wb").write(uncrypted)

        image_format = get_image_type(uncrypted)
        store_path_converted = f"{save_path}/{title_used} {page_txt}.{image_format}"
        if os.path.exists(store_path_converted):
            os.remove(store_path_converted)
        os.rename(store_path, store_path_converted)

        if pause_sec:
            await asyncio.sleep(pause_sec)
        return store_path_converted

    async def _async_download_all_pages(
        self,
        title_used: str,
        save_path: str,
    ) -> List[str]:
        book_infos = self.get_book_infos()
        if len(book_infos.page_urls) == 0:
            return []
        return await tqdm.gather(
            *[
                self._async_download_page(
                    page_num=page,
                    url=url,
                    title_used=title_used,
                    save_path=save_path,
                    pause_sec=0,
                )
                for page, url in enumerate(book_infos.page_urls)
            ],
            desc="Download pages",
            bar_format=BAR_FORMAT,
        )

    def _download_all_pages(self, title_used: str, save_path: str) -> List[str]:
        book_infos = self.get_book_infos()
        downloaded_pages: List[str] = []
        if len(book_infos.page_urls) == 0:
            return downloaded_pages
        for page, url in tqdm(
            enumerate(book_infos.page_urls),
            desc="Download pages",
            bar_format=BAR_FORMAT,
            total=len(book_infos.page_urls),
        ):
            res = asyncio.run(
                self._async_download_page(
                    page_num=page,
                    url=url,
                    title_used=title_used,
                    save_path=save_path,
                    pause_sec=self.config.pause_sec or 0,
                )
            )
            downloaded_pages.append(res)
        return downloaded_pages

    def _create_destination_folder(self, save_path: str) -> None:
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        print(f"Destination : {save_path}")

    def create_output_folder(
        self, book_infos: BookInfos, output_folder: Optional[str]
    ) -> str:
        if not output_folder:
            output_folder = "DOWNLOADS"
        output_folder = get_name_from_pattern(output_folder, book_infos)
        output_folder = clean_name(output_folder, directory=True)
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def _get_title_to_use(self, book_infos: BookInfos) -> str:
        return get_name_from_pattern(
            self.config.output_filename or "", book_infos
        ) or self.get_default_title(book_infos)

    def get_default_title(self, book_infos: BookInfos) -> str:
        title_used = book_infos.title
        subtitle = book_infos.subtitle or ""
        volume = book_infos.volume or ""
        if len(subtitle) > 0:
            title_used = f"{book_infos.title} - {subtitle}"
            if len(volume) > 0:
                title_used = f'{book_infos.title} - {f"00000{volume}"[-max(2, len(volume)):]}. {subtitle}'
        if len(subtitle) == 0 and len(volume) > 0:
            title_used = (
                f'{book_infos.title} - {f"00000{volume}"[-max(2, len(volume)):]}'
            )
        return title_used


def init(url: str = "", config: Optional[Config] = None) -> SiteProcessor:
    return SiteProcessor(url, config)
