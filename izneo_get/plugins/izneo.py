# -*- coding: utf-8 -*-
from typing import Dict, List, Optional
import requests
import re
import os
import json
from Crypto.Cipher import AES
import base64
import urllib.parse
import asyncio
from tqdm.asyncio import tqdm
from functools import lru_cache
from ..tools import (
    requests_retry_session,
    clean_name,
    get_image_type,
    get_name_from_pattern,
    clean_attribute,
    async_http_get,
    convert_image_if_needed,
    question_yes_no,
    BAR_FORMAT,
)
from ..config import Config, ImageFormat, OutputFormat
from ..book_infos import BookInfos, ReadDirection
from .site_processor import SiteProcessor


class Izneo(SiteProcessor):
    URL_PATTERNS: List[str] = [
        r"https://reader\.izneo\.com/read/(\d+)(\?exiturl=.+)?",
        r"https://www.izneo.com/(.+?)/(.+?)/(.+?)/(.+?)-(\d+)/(.+)-(\d+)",
        r"https://www.izneo.com/(.+?)/(.+?)/(.+?)(\?exiturl=.+)?",
    ]
    url: str = ""
    config: Config
    cache_file: str = "izneo.cache"

    session: Optional[requests.Session] = None
    headers: Dict[str, str] = {}
    root_path = "https://www.izneo.com/"

    _book_infos: Optional[BookInfos] = None

    def __init__(self, url: str = "", config: Optional[Config] = None) -> None:
        super().__init__(url=url, config=config)
        self.url = self._clean_url(self.url)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return any(re.match(pattern, url) is not None for pattern in Izneo.URL_PATTERNS)

    def authenticate(self) -> None:
        if self.config.authentication_from_cache:
            session_id = self._authenticate_from_cache()
        else:
            session_id = self._authenticate_from_prompt()
        self._init_session(session_id)

    def _authenticate_from_prompt(self) -> str:
        session_id = ""
        while not session_id:
            session_id = input('Session ID (value of cookie named "c03aab1711dbd2a02ea11200dde3e3d1"): ')
        self._save_cache(session_id)
        return session_id

    def _authenticate_from_cache(self) -> str:
        session_id = None
        cache_file = f"{self.config.cache_folder}/{self.cache_file}"
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                session_id = f.read()
            return session_id
        return self._authenticate_from_prompt()

    def _save_cache(self, session_id: str) -> None:
        cache_folder = self.config.cache_folder or "."
        os.makedirs(cache_folder, exist_ok=True)
        cache_file = f"{cache_folder}/{self.cache_file}"
        with open(cache_file, "w") as f:
            f.write(session_id)

    def _clean_url(self, url: str) -> str:
        if res := re.search(r"exiturl=(.+?)\&", url):
            replace_from = res[1]
            replace_to = urllib.parse.quote_plus(replace_from)
            url = url.replace(replace_from, replace_to)
            url = url.replace("%25", "%")
        return url

    def _init_session(self, session_id: str) -> None:
        """Create session with cookie corresponding to your account session.

        Args:
            session_id (str): value found in the cookie named "c03aab1711dbd2a02ea11200dde3e3d1".
        """
        # Create session and cookie.
        self.session = requests.Session()
        self.session.max_redirects = 10
        cookie_obj = requests.cookies.create_cookie(domain=".izneo.com", name="lang", value="fr")
        self.session.cookies.set_cookie(cookie_obj)
        cookie_obj = requests.cookies.create_cookie(
            domain=".izneo.com", name="c03aab1711dbd2a02ea11200dde3e3d1", value=session_id
        )
        self.session.cookies.set_cookie(cookie_obj)

    def download(self, forced_title: Optional[str] = None) -> str:
        book_infos = self.get_book_infos()

        if book_infos.custom_fields and book_infos.custom_fields["state"] == "preview":
            print(f"WARNING: with your credentials, only preview is available ({book_infos.pages} pages).")
            answer = question_yes_no("Continue anyway", default=False)
            if answer == False:
                return ""
        return super().download(forced_title)

    def post_process_image_content(self, content: bytes, page_num: int = 0) -> bytes:
        book_infos = self.get_book_infos()
        if self._get_signature():
            return content
        if not book_infos or not book_infos.custom_fields:
            return content
        key = book_infos.custom_fields["pages"][page_num]["key"]
        iv = book_infos.custom_fields["pages"][page_num]["iv"]
        return Izneo.uncrypt_image(content, key, iv)

    @staticmethod
    def uncrypt_image(crypted_content: bytes, key: str, iv: str) -> bytes:
        aes = AES.new(base64.b64decode(key), AES.MODE_CBC, base64.b64decode(iv))
        return aes.decrypt(crypted_content)

    def get_book_infos(self) -> BookInfos:
        if self._book_infos:
            return self._book_infos
        book_id = self._get_book_id()
        sign = self._get_signature()

        book_infos = self._download_book_infos()
        book_infos = book_infos if isinstance(book_infos, dict) else {}
        title = clean_attribute(book_infos.get("title", ""))
        subtitle = clean_attribute(book_infos.get("subtitle", ""))
        read_direction = ReadDirection.RTOL if book_infos.get("readDirection", "") == "rtl" else ReadDirection.LTOR
        page_urls = []
        for page_num, _ in enumerate(book_infos.get("pages", None)):
            url = f"https://www.izneo.com/book/{book_id}/{page_num}?type=full" + (f"&{sign}" if sign else "")
            if sign:
                url = f"https://reader.izneo.com/read/{book_id}/{page_num}?quality=HD" + (f"&{sign}" if sign else "")
            page_urls.append(url)

        self._book_infos = BookInfos(
            title=title,
            subtitle=subtitle,
            pages=int(book_infos.get("nbPage", 0)),
            volume=book_infos.get("volume", ""),
            chapter=book_infos.get("chapter", ""),
            isbn=book_infos.get("ean", ""),
            serie=book_infos.get("serie_name", ""),
            genre=book_infos.get("gender_name", ""),
            language=book_infos.get("userLang", ""),
            read_direction=read_direction,
            description=book_infos.get("synopsis", ""),
            page_urls=page_urls,
            custom_fields={"pages": book_infos.get("pages", None), "state": book_infos.get("state", "")},
        )
        return self._book_infos

    def _download_book_infos(self):
        book_id = self._get_book_id()
        sign = self._get_signature()
        cookies = self.session.cookies if self.session else None
        r = requests_retry_session(session=self.session).get(
            f"https://www.izneo.com/book/{book_id}" + (f"?{sign}" if sign else ""),
            cookies=cookies,
            allow_redirects=True,
            headers=self.headers,
        )
        data = json.loads(r.text)["data"]
        if sign:
            full_page = requests_retry_session(session=self.session).get(
                f"https://reader.izneo.com/read/{book_id}",
                cookies=cookies,
                allow_redirects=True,
                headers=self.headers,
            )
            if full_page.status_code == 200 and full_page.text:
                if res := re.search(r"unrestrictedBoardsCount([\s])+=([\s\d]+);", full_page.text):
                    total_pages = int(res[2])
                    data["nbPage"] = total_pages
                    data["state"] = "signed"
                    data["pages"] = list(range(total_pages))
        return data

    @lru_cache
    def _get_book_id(self) -> str:
        book_id = ""
        # URL direct.
        if res := re.search(r"(.+)reader\.(.+)/read/(.+)", self.url):
            book_id = res[3]
            if res := re.search(r"(.+)\?(.*)", book_id):
                book_id = res[1]

        # On teste si c'est une page de description ou une page de lecture.
        tmp_url = self.url
        if res := re.search("(.+)/read/(.+)", self.url):
            tmp_url = res[1]
        if res := re.search(".+-(.+)/read", tmp_url.split("?")[0]):
            book_id = res[1]
        elif res := re.search(".+-(.+)", tmp_url.split("?")[0]):
            book_id = res[1]
        elif res := re.search(".+/(.+)", self.url.split("?")[0]):
            book_id = res[1]
        return book_id

    @lru_cache
    def _get_signature(self) -> str:
        sign = ""
        if res := re.match("(.+)login=cvs&sign=([^&]*)", self.url):
            sign = res[2]
            sign = f"login=cvs&sign={sign}"
        return sign


def init(url: str = "", config: Optional[Config] = None) -> Izneo:
    return Izneo(url, config)
