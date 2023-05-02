from typing import Dict, List
import requests
import re
import os
import sys
import html
import time
from PIL import Image
import json
from Crypto.Cipher import AES
import base64
import urllib.parse
import asyncio
from tqdm.asyncio import tqdm
from ..tools import (
    requests_retry_session,
    clean_name,
    get_image_type,
    get_name_from_pattern,
    clean_attribute,
    async_http_get,
    convert_image_if_needed,
    question_yes_no,
)
from ..config import Config, ImageFormat, OutputFormat
from ..book_infos import BookInfos, ReadDirection
from .site_processor import SiteProcessor

BAR_FORMAT = "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"  # Progress bar format


class Izneo(SiteProcessor):
    URL_PATTERNS: List[str] = [
        r"https://reader\.izneo\.com/read/(\d+)(\?exiturl=.+)?",
        r"https://www.izneo.com/(.+?)/(.+?)/(.+?)/(.+?)-(\d+)/(.+)-(\d+)",
    ]
    url: str = ""
    config: Config
    cache_file: str = "izneo.cache"

    session: requests.Session = None
    headers: dict = {}
    root_path = "https://www.izneo.com/"

    __book_infos: BookInfos = None
    __sign: str = None
    __book_id: str = None

    def __init__(self, url: str = "", config: Config = None):
        super().__init__(url=url, config=config)
        self.url = self.__clean_url(self.url)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return any(re.match(pattern, url) is not None for pattern in Izneo.URL_PATTERNS)

    def authenticate(self) -> None:
        if self.config.authentication_from_cache:
            session_id = self.__authenticate_from_cache()
        else:
            session_id = self.__authenticate_from_prompt()
        self.__init_session(session_id)

    def __authenticate_from_prompt(self) -> str:
        session_id = ""
        while not session_id:
            session_id = input('Session ID (value of cookie named "c03aab1711dbd2a02ea11200dde3e3d1"): ')
        self.__save_cache(session_id)
        return session_id

    def __authenticate_from_cache(self) -> str:
        session_id = None
        cache_file = f"{self.config.cache_folder}/{self.cache_file}"
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                session_id = f.read()
            return session_id
        return self.__authenticate_from_prompt()

    def __save_cache(self, session_id: str) -> None:
        os.makedirs(self.config.cache_folder, exist_ok=True)
        cache_file = f"{self.config.cache_folder}/{self.cache_file}"
        with open(cache_file, "w") as f:
            f.write(session_id)

    def __clean_url(self, url: str) -> str:
        if res := re.search(r"exiturl=(.+?)\&", url):
            replace_from = res[1]
            replace_to = urllib.parse.quote_plus(replace_from)
            url = url.replace(replace_from, replace_to)
            url = url.replace("%25", "%")
        return url

    def __init_session(self, session_id: str) -> None:
        # Create session and cookie.
        self.session = requests.Session()
        cookie_obj = requests.cookies.create_cookie(domain=".izneo.com", name="lang", value="fr")
        self.session.cookies.set_cookie(cookie_obj)
        cookie_obj = requests.cookies.create_cookie(
            domain=".izneo.com", name="c03aab1711dbd2a02ea11200dde3e3d1", value=session_id
        )
        self.session.cookies.set_cookie(cookie_obj)

    def download(self, forced_title: str = None) -> str:
        print(f"URL: {self.url}")
        book_id = self.__get_book_id()
        book_infos = self.get_book_infos()
        sign = self.__get_signature()

        if book_infos.custom_fields["state"] == "preview":
            print(f"WARNING: with your credentials, only preview is available ({book_infos.pages} pages).")
            answer = question_yes_no("Continue anyway", default=False)
            if answer == False:
                return ""

        # Si on n'a pas les informations de base, on arrête tout de suite.
        if not book_infos.title or not book_infos.pages:
            print("ERROR: Can't find book.")
            return ""

        # Création du répertoire de destination.
        output_folder = self.create_output_folder(book_infos, self.config.output_folder)

        title_used = self.__get_title_to_use(book_infos)

        if forced_title:
            forced_title = get_name_from_pattern(forced_title, book_infos)
            print(f'Download "{clean_name(title_used)}" as "{clean_name(forced_title)}"')
            title_used = clean_name(forced_title)
        else:
            print(f'Download "{clean_name(title_used)}"')
        save_path = f"{output_folder}/{clean_name(title_used)}"

        print(f"{book_infos.pages} pages expected")

        # Si l'archive existe déjà, on ne télécharge pas cette BD.
        if (
            self.config.continue_from_existing
            and self.config.output_format == OutputFormat.CBZ
            and os.path.exists(f"{save_path}.cbz")
        ):
            print(f'"{save_path}.cbz" already exists, skipping.')
            return f"{save_path}.cbz"
        self.__create_destination_folder(save_path)

        files_downloaded: List[str] = []
        if self.config.pause_sec:
            files_downloaded = self.__download_all_pages(title_used, save_path)
        else:
            files_downloaded = asyncio.run(self.__async_download_all_pages(title_used, save_path))
        return save_path, files_downloaded

    async def __async_download_page(self, page_num: int, title_used: str, save_path: str, pause_sec: int = 0) -> str:
        book_id = self.__get_book_id()
        sign = self.__get_signature()
        book_infos = self.get_book_infos()

        nb_digits = max(3, len(str(len(book_infos.custom_fields["pages"]))))
        url = f"https://www.izneo.com/book/{book_id}/{page_num}?type=full" + (f"&{sign}" if sign else "")

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
        r = await async_http_get(url, session=self.session, headers=self.headers)

        if r.status_code == 404:
            if page_num < book_infos.pages:
                print(f"[WARNING] Can't download page {str(page_num + 1)} ({str(book_infos.pages)} pages expected)")
            return ""
        if r.encoding:
            print(f"[WARNING] Page {page_num} unavailable")
            return ""

        # Decode image.
        key = book_infos.custom_fields["pages"][page_num]["key"]
        iv = book_infos.custom_fields["pages"][page_num]["iv"]
        uncrypted = Izneo.uncrypt_image(r.content, key, iv)
        store_path = f"{save_path}/{title_used} {page_txt}.tmp"
        open(store_path, "wb").write(uncrypted)

        image_format = get_image_type(uncrypted)
        if self.config.image_format == ImageFormat.ORIGIN:
            store_path_converted = f"{save_path}/{title_used} {page_txt}.{image_format}"

        # Convert image if needed.
        convert_image_if_needed(store_path, store_path_converted, self.config.image_format, self.config.image_quality)
        if pause_sec:
            await asyncio.sleep(pause_sec)
        return store_path_converted

    @staticmethod
    def uncrypt_image(crypted_content: bytes, key, iv) -> bytes:
        aes = AES.new(base64.b64decode(key), AES.MODE_CBC, base64.b64decode(iv))
        return aes.decrypt(crypted_content)

    async def __async_download_all_pages(self, title_used: str, save_path: str) -> None:
        book_infos = self.get_book_infos()
        return await tqdm.gather(
            *[
                self.__async_download_page(page, title_used, save_path)
                for page in range(len(book_infos.custom_fields["pages"]))
            ],
            desc="Download pages",
            bar_format=BAR_FORMAT,
        )

    def __download_all_pages(self, title_used: str, save_path: str) -> None:
        book_infos = self.get_book_infos()
        downloaded_pages = []
        for page in tqdm(
            range(len(book_infos.custom_fields["pages"])),
            desc="Download pages",
            bar_format=BAR_FORMAT,
        ):
            res = asyncio.run(self.__async_download_page(page, title_used, save_path, self.config.pause_sec))
            downloaded_pages.append(res)
        return downloaded_pages

    def __create_destination_folder(self, save_path):
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        print(f"Destination : {save_path}")

    def __get_title_to_use(self, book_infos):
        return get_name_from_pattern(self.config.output_filename, book_infos) or self.get_default_title(book_infos)

    def get_book_infos(self) -> BookInfos:
        if self.__book_infos:
            return self.__book_infos
        book_infos = self.__download_book_infos()
        title = clean_attribute(book_infos["title"])
        subtitle = clean_attribute(book_infos["subtitle"])
        read_direction = ReadDirection.RTOL if book_infos["readDirection"] == "rtl" else ReadDirection.LTOR
        self.__book_infos = BookInfos(
            title=title,
            subtitle=subtitle,
            pages=int(book_infos["nbPage"]),
            volume=book_infos["volume"],
            chapter=book_infos["chapter"],
            isbn=book_infos["ean"],
            serie=book_infos["serie_name"],
            genre=book_infos["gender_name"],
            language=book_infos["userLang"],
            read_direction=read_direction,
            description=book_infos["synopsis"],
            custom_fields={"pages": book_infos["pages"], "state": book_infos["state"]},
        )
        return self.__book_infos

    def __download_book_infos(self):
        book_id = self.__get_book_id()
        sign = self.__get_signature()
        cookies = self.session.cookies if self.session else None
        r = requests_retry_session(session=self.session).get(
            f"https://www.izneo.com/book/{book_id}" + (f"?{sign}" if sign else ""),
            cookies=cookies,
            allow_redirects=True,
            headers=self.headers,
        )
        return json.loads(r.text)["data"]

    def __get_book_id(self) -> int:
        if self.__book_id:
            return self.__book_id
        book_id = ""
        # URL direct.
        if res := re.search("(.+)reader\.(.+)/read/(.+)", self.url):
            book_id = res[3]
            if res := re.search("(.+)\?(.*)", book_id):
                book_id = res[1]

        # On teste si c'est une page de description ou une page de lecture.
        tmp_url = self.url
        if res := re.search("(.+)/read/(.+)", self.url):
            tmp_url = res[1]
        if res := re.search(".+-(.+)/read", tmp_url.split("?")[0]):
            book_id = res[1]
        elif res := re.search(".+-(.+)", tmp_url.split("?")[0]):
            book_id = res[1]
        self.__book_id = book_id
        return self.__book_id

    def __get_signature(self) -> str:
        if self.__sign is not None:
            return self.__sign
        sign = ""
        if re.match("(.+)login=cvs&sign=([^&]*)", self.url):
            sign = re.match("(.+)login=cvs&sign=([^&]*)", self.url)[2]
            sign = f"login=cvs&sign={sign}"
        self.__sign = sign
        return self.__sign


def init(url: str = "", config: Config = None) -> Izneo:
    return Izneo(url, config)
