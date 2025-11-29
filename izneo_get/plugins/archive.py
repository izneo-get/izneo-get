# -*- coding: utf-8 -*-
import asyncio
import base64
import hashlib
import os
import random
import re
from functools import lru_cache
from http.cookiejar import LWPCookieJar
from typing import Dict, List, Optional

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ..book_infos import BookInfos, ReadDirection
from ..config import Config, OutputFormat
from ..tools import (
    BAR_FORMAT,
    async_http_get,
    clean_attribute,
    clean_name,
    convert_image_if_needed,
    generate_random_string,
    get_image_type,
    get_name_from_pattern,
    http_post,
    question_yes_no,
    requests_retry_session,
)
from .site_processor import SiteProcessor


class Archive(SiteProcessor):
    URL_PATTERNS = ["https://archive.org/details/.*"]
    url: str = ""
    config: Config
    cache_file: str = "archive.cache"

    session: Optional[requests.Session] = None
    headers: Dict[str, str] = {}
    root_path = "https://archive.org/"
    _book_infos: Optional[BookInfos] = None

    def __init__(self, url: str = "", config: Optional[Config] = None):
        super().__init__(url, config)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return any(
            re.match(pattern, url) is not None for pattern in Archive.URL_PATTERNS
        )

    def authenticate(self) -> None:
        if self.config.authentication_from_cache:
            self._authenticate_from_cache()
        else:
            self._authenticate_from_prompt()

    def _authenticate_from_prompt(self) -> None:
        print('INFO: Authentication to "archive.org" required.')
        email = ""
        while not email:
            email = input("Email: ")
        password = ""
        while not password:
            password = input("Password: ")
        self._authenticate_from_email(email, password)
        # Not a typo, we need to authenticate again to get the session right.
        self._authenticate_from_email(email, password)

    def data_to_boundary(self, boundary: str, data: Dict) -> str:
        body = []
        for key, value in data.items():
            body.extend(
                (
                    f"--{boundary}",
                    f'Content-Disposition: form-data; name="{key}"',
                    "",
                    value,
                )
            )
        return "\r\n".join(body) + f"\r\n--{boundary}--\r\n"

    def _authenticate_from_email(self, email: str, password: str) -> None:
        boundary = f"----WebKitFormBoundary{generate_random_string(16)}"
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        data = {"username": email, "password": password, "submit_by_js": "true"}
        data = self.data_to_boundary(boundary, data)
        if not self.session:
            self._init_session()
        response = self.session.post(
            "https://archive.org/account/login", data=data, headers=headers
        )
        if response.status_code != 200:
            print("ERROR: Can't authenticate")
            exit()
        self.session.cookies.save(ignore_discard=True)

    def _authenticate_from_cache(self) -> None:
        os.makedirs(self.config.cache_folder, exist_ok=True)
        cache_file = f"{self.config.cache_folder}/{self.cache_file}"
        self.session = requests.Session()
        self.session.cookies = LWPCookieJar(filename=cache_file)
        try:
            self.session.cookies.load(ignore_discard=True)
        except FileNotFoundError:
            return self._authenticate_from_prompt()

    def _init_session(self) -> None:
        # Create session and cookie.
        self.session = requests.Session()
        self.session.max_redirects = 10
        cache_folder = self.config.cache_folder or "."
        os.makedirs(cache_folder, exist_ok=True)
        cache_file = f"{cache_folder}/{self.cache_file}"
        self.session.cookies = LWPCookieJar(filename=cache_file)

    def get_book_infos(self) -> BookInfos:
        if self._book_infos:
            return self._book_infos
        book_infos = self._download_book_infos()
        book_infos = book_infos if isinstance(book_infos, dict) else {}
        title = clean_attribute(book_infos["brOptions"].get("bookTitle", ""))
        # subtitle = clean_attribute(book_infos["brOptions"].get("subPrefix", ""))
        subtitle = ""
        read_direction = (
            ReadDirection.RTOL
            if book_infos["brOptions"].get("pageProgression", "") == "rl"
            else ReadDirection.LTOR
        )
        page_urls = [
            page["uri"] + "&rotate=0&scale=0"
            for item in book_infos["brOptions"]["data"]
            for page in item
        ]

        self._book_infos = BookInfos(
            title=title,
            subtitle=subtitle,
            pages=len(page_urls),
            authors=book_infos["metadata"].get("creator", ""),
            genre=book_infos["metadata"].get("subject", ""),
            language=book_infos["metadata"].get("language", ""),
            read_direction=read_direction,
            description=book_infos["metadata"].get("description", ""),
            page_urls=page_urls,
            custom_fields={
                "metadata": book_infos["metadata"],
                "book_id": book_infos["brOptions"]["bookId"],
            },
        )
        return self._book_infos

    def before_download(self) -> None:
        self.authenticate()
        self.loan()
        self.headers = {
            "Referer": "https://archive.org/",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "image",
        }

    def after_download(self, files_downloaded: List[str]) -> None:
        self.return_loan()

    def loan(self):
        book_id = self._get_book_id()

        data = {"action": "grant_access", "identifier": book_id}
        response = self.session.post(
            "https://archive.org/services/loans/loan/searchInside.php", data=data
        )
        if response.status_code != 200 or not response.json()["success"]:
            print(f"ERROR: Can't loan: {response.status_code}")

        boundary = f"----WebKitFormBoundary{generate_random_string(16)}"
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        data = {"action": "browse_book", "identifier": book_id}
        data = self.data_to_boundary(boundary, data)
        response = self.session.post(
            "https://archive.org/services/loans/loan/", headers=headers, data=data
        )

        if response.status_code == 401 and response.reason == "Unauthorized":
            print("ERROR: Can't loan. Session expired?")
            self._authenticate_from_prompt()
            return self.loan()

        data = {"action": "create_token", "identifier": book_id}
        data = self.data_to_boundary(boundary, data)
        response = self.session.post(
            "https://archive.org/services/loans/loan/", data=data, headers=headers
        )
        if "token" in response.text:
            self._book_infos = None
            self.get_book_infos()
            print(f"INFO: Book loaned: {self._book_infos.title}")

    def return_loan(self):
        book_id = self._get_book_id()
        data = {"action": "return_loan", "identifier": book_id}
        response = self.session.post(
            "https://archive.org/services/loans/loan/", data=data
        )
        if response.status_code == 200 and response.json()["success"]:
            print(f"INFO: Book returned: {self._book_infos.title}")

    def _download_book_infos(self) -> Dict:
        cookies = self.session.cookies if self.session else None
        r = requests_retry_session(session=self.session).get(
            self.url,
            cookies=cookies,
            allow_redirects=True,
            headers=self.headers,
        )
        if r.status_code != 200:
            print(f"ERROR: Can't get book infos: {r.status_code}")
            exit()
        res = re.search(r'"url":"(.*)"', r.text)
        if not res:
            print("ERROR: Can't get book infos")
            exit()
        infos_url = f"https:{res[1]}".replace("\\u0026", "&")
        r = requests_retry_session(session=self.session).get(
            infos_url,
            cookies=cookies,
            allow_redirects=True,
            headers=self.headers,
        )
        if r.status_code != 200:
            print(f"ERROR: Can't get book infos: {r.status_code}")
            exit()
        return r.json()["data"]

    @lru_cache
    def _get_book_id(self) -> str:
        book_infos = self.get_book_infos()
        return (
            book_infos.custom_fields.get("book_id", "")
            if book_infos.custom_fields
            else ""
        )

    def post_process_image_content(
        self, response: requests.models.Response, page_num: int = 0
    ) -> bytes:
        obfuscation_header = response.headers.get("x-obfuscate")
        if not obfuscation_header:
            return response.content

        try:
            version, counter_b64 = obfuscation_header.split("|")
            if version != "1":
                raise ValueError(f"Unsupported obfuscation version: {version}")
        except ValueError as e:
            print(f"Obfuscation error: {e}")
            return response.content

        aes_key = "/" + "/".join(response.url.split("/")[3:])
        image_buffer = response.content

        DECRYPT_SIZE = 1024

        if len(image_buffer) < DECRYPT_SIZE:
            print(f"Error: Image too small ({len(image_buffer)} octets)")
            return

        encrypted_fragment = image_buffer[:DECRYPT_SIZE]
        remaining_image = image_buffer[DECRYPT_SIZE:]

        try:
            decrypted_fragment = decrypt_data(encrypted_fragment, aes_key, counter_b64)
        except Exception as e:
            print(f"Error: {e}")
            return

        decrypted_image_buffer = decrypted_fragment + remaining_image

        return decrypted_image_buffer


def decrypt_data(buffer_fragment: bytes, aes_key: str, counter_b64: str) -> bytes:
    """
    Decrypts a data fragment using AES-CTR, reproducing the JS logic.

    Args:
        buffer_fragment: The binary fragment to decrypt (the first 1024 bytes).
        aes_key: The AES key string (the URI path).
        counter_b64: The counter encoded in Base64 from the X-Obfuscate header.

    Returns:
        The decrypted binary data.
    """
    # 1. Hash the key with SHA-1 and truncate
    sha1_hash = hashlib.sha1(aes_key.encode("utf-8")).digest()

    # 2. Use the first 16 bytes of the SHA-1 hash as AES key
    key = sha1_hash[:16]  # Key of 16 bytes for AES-128

    # 3. Decode the counter Base64
    try:
        iv_counter = base64.b64decode(counter_b64)
    except Exception as e:
        raise ValueError(f"Error: Base64 counter decoding failed: {e}")

    # Verify the size of the counter/IV (must be 16 bytes for AES-CTR)
    if len(iv_counter) != 16:
        # The counter size must be 16 bytes (128 bits) for AES-CTR mode
        # The specified 64-bit length in JS is not consistent with the 16-byte IV
        # The JS implementation seems to use the first 8 bytes as IV and the next 8 as counter.
        # We will assume that the complete IV is the Base64 decoded 16 bytes.
        # If the decoded counter is not 16 bytes, it could indicate a JS implementation issue
        # or non-standard encoding. In doubt, we assume 16 bytes.
        print(
            f"Warning: Decoded counter length: {len(iv_counter)} bytes (expected 16)."
        )

    # 4. AES-CTR decryption
    # length: 64 in JS indicates a 64-bit segment to use as counter,
    # which is the default for many 16-byte IVs.
    cipher = Cipher(
        algorithms.AES(key), modes.CTR(iv_counter), backend=default_backend()
    )

    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(buffer_fragment) + decryptor.finalize()

    return decrypted_data


def init(url: str = "", config: Optional[Config] = None) -> Archive:
    return Archive(url, config)
