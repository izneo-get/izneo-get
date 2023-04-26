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
from ..tools import requests_retry_session, clean_name, get_image_type, get_name_from_pattern, clean_attribute
from ..config import Config, ImageFormat, OutputFormat
from ..book_infos import BookInfos, ReadDirection
from .site_processor import SiteProcessor


class Izneo(SiteProcessor):
    URL_PATTERNS: List[str] = [
        r"https://reader\.izneo\.com/read/(\d+)(\?exiturl=.+)?",
        r"https://www.izneo.com/(.+?)/(.+?)/(.+?)/(.+?)-(\d+)/(.+)-(\d+)",
    ]
    url: str = ""
    config: Config

    session: requests.Session = None
    headers: dict = {}
    root_path = "https://www.izneo.com/"
    cache_file: str = "izneo.cache"

    _book_infos: BookInfos = None
    _sign: str = None
    _book_id: str = None

    def __init__(self, url: str = "", config: Config = None):
        super().__init__(url=url, config=config)
        self.url = self.clean_url(self.url)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        # return super().is_valid_url(url)
        return any(re.match(pattern, url) is not None for pattern in Izneo.URL_PATTERNS)

    def authenticate(self) -> None:
        if self.config.authentication_from_cache:
            session_id = self.authenticate_from_cache()
        else:
            session_id = self.authenticate_from_prompt()
        self.init_session(session_id)

    def authenticate_from_prompt(self) -> str:
        session_id = ""
        while not session_id:
            session_id = input("Session ID: ")
        self.save_cache(session_id)
        return session_id

    def authenticate_from_cache(self) -> str:
        session_id = None
        cache_file = f"{self.config.cache_folder}/{self.cache_file}"
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                session_id = f.read()
            return session_id
        return self.authenticate_from_prompt()

    def save_cache(self, session_id: str) -> None:
        os.makedirs(self.config.cache_folder, exist_ok=True)
        cache_file = f"{self.config.cache_folder}/{self.cache_file}"
        with open(cache_file, "w") as f:
            f.write(session_id)

    def clean_url(self, url: str) -> str:
        if res := re.search(r"exiturl=(.+?)\&", url):
            replace_from = res[1]
            replace_to = urllib.parse.quote_plus(replace_from)
            url = url.replace(replace_from, replace_to)
            url = url.replace("%25", "%")
        return url

    def init_session(self, session_id: str) -> None:
        # Création d'une session et création du cookie.
        self.session = requests.Session()
        cookie_obj = requests.cookies.create_cookie(domain=".izneo.com", name="lang", value="fr")
        self.session.cookies.set_cookie(cookie_obj)
        cookie_obj = requests.cookies.create_cookie(
            domain=".izneo.com", name="c03aab1711dbd2a02ea11200dde3e3d1", value=session_id
        )
        self.session.cookies.set_cookie(cookie_obj)

    def download(self, forced_title: str = None) -> str:
        print(f"URL: {self.url}")
        sign = self.get_signature()
        book_id = self.get_book_id()

        # Récupération des informations de la BD.
        book_infos = self.get_book_infos()
        page_sup_to_grab = 0
        # Le nombre de pages annoncé.
        nb_digits = max(3, len(str(book_infos.pages + page_sup_to_grab)))

        # Si on n'a pas les informations de base, on arrête tout de suite.
        if not book_infos.title or not book_infos.pages:
            print("ERROR Impossible de trouver le livre")
            return ""

        # Création du répertoire de destination.
        output_folder = self.create_output_folder(book_infos, self.config.output_folder)

        title_used = get_name_from_pattern(self.config.output_filename, book_infos)
        if not title_used:
            title_used = self.get_default_title(book_infos)

        if forced_title:
            forced_title = get_name_from_pattern(forced_title, book_infos)
            print(f'Téléchargement de "{clean_name(title_used)}" en tant que "{clean_name(forced_title)}"')
            title_used = clean_name(forced_title)
        else:
            print(f'Téléchargement de "{clean_name(title_used)}"')
        save_path = f"{output_folder}/{clean_name(title_used)}"

        print(f"{book_infos.pages} pages attendues")

        # Si l'archive existe déjà, on ne télécharge pas cette BD.
        if (
            self.config.continue_from_existing
            and self.config.output_format == OutputFormat.CBZ
            and os.path.exists(f"{save_path}.cbz")
        ):
            print(f"{save_path}.cbz existe déjà, on passe")
            return f"{save_path}.cbz"
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        print(f"Destination : {save_path}")

        progress_bar = ""
        # On boucle sur toutes les pages de la BD.
        nb_page_limit = 1000000
        from_page = 0
        for page in range(min(book_infos.pages + page_sup_to_grab, nb_page_limit)):
            page_num = page + from_page

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
                progress_bar += "x"
                progress_message = (
                    "\r" + "[page " + str(page_num + 1) + " / ~" + str(book_infos.pages) + "] " + progress_bar + " "
                )
                # print("x", end="")
                print(progress_message, end="")
                sys.stdout.flush()
                continue

            # r = s.get(url, cookies=s.cookies, allow_redirects=True, params=params, headers=headers)
            r = requests_retry_session(session=self.session).get(
                url,
                cookies=self.session.cookies,
                allow_redirects=True,
                headers=self.headers,
            )

            if r.status_code == 404:
                if page < book_infos.pages:
                    print(
                        f"[WARNING] On a récupéré {str(page + 1)} pages ({str(book_infos.pages)} annoncées par l'éditeur)"
                    )
                break
            # if re.findall("<!DOCTYPE html>", r.text):
            # if "<!DOCTYPE html>" in r.text:
            if r.encoding:
                print(f"[WARNING] Page {str(page_num)} inaccessible")
                break

            # On déchiffre l'image.

            key = book_infos.custom_fields["pages"][page_num]["key"]
            iv = book_infos.custom_fields["pages"][page_num]["iv"]
            aes = AES.new(base64.b64decode(key), AES.MODE_CBC, base64.b64decode(iv))
            uncrypted = aes.decrypt(r.content)
            image_format = get_image_type(uncrypted)

            if self.config.image_format == ImageFormat.ORIGIN:
                store_path_converted = f"{save_path}/{title_used} {page_txt}.{image_format}"

            store_path = f"{save_path}/{title_used} {page_txt}.tmp"
            open(store_path, "wb").write(uncrypted)
            # Si demandé, on converti.
            if self.config.image_format == ImageFormat.WEBP:
                im = Image.open(store_path)
                im.save(store_path_converted, "webp", quality=self.config.image_quality)
                os.remove(store_path)
            if self.config.image_format == ImageFormat.JPEG:
                im = Image.open(store_path)
                im.save(store_path_converted, "jpeg", quality=self.config.image_quality)
                os.remove(store_path)
            if self.config.image_format == ImageFormat.ORIGIN:
                if os.path.exists(store_path_converted):
                    os.remove(store_path_converted)
                os.rename(store_path, store_path_converted)
            progress_bar += "."
            progress_message = (
                "\r" + "[page " + str(page_num + 1) + " / ~" + str(book_infos.pages) + "] " + progress_bar + " "
            )
            # print(".", end="")
            print(progress_message, end="")
            sys.stdout.flush()
            time.sleep(self.config.pause_sec)
        return save_path

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

    def create_output_folder(self, book_infos: BookInfos, output_folder: str = "DOWNLOADS") -> str:
        output_folder = get_name_from_pattern(self.config.output_folder, book_infos)
        output_folder = clean_name(output_folder, directory=True)
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def get_book_infos(self) -> BookInfos:
        if self._book_infos:
            return self._book_infos
        book_infos = self.download_book_infos()
        title = clean_attribute(book_infos["title"])
        subtitle = clean_attribute(book_infos["subtitle"])
        read_direction = ReadDirection.RTOL if book_infos["readDirection"] == "rtl" else ReadDirection.LTOR
        self._book_infos = BookInfos(
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
            custom_fields={"pages": book_infos["pages"]},
        )
        return self._book_infos

    def download_book_infos(self):
        book_id = self.get_book_id()
        sign = self.get_signature()
        r = requests_retry_session(session=self.session).get(
            f"https://www.izneo.com/book/{book_id}" + (f"?{sign}" if sign else ""),
            cookies=self.session.cookies,
            allow_redirects=True,
            headers=self.headers,
        )
        return json.loads(r.text)["data"]

    def get_book_id(self):
        if self._book_id:
            return self._book_id
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
        self._book_id = book_id
        return self._book_id

    def get_signature(self):
        if self._sign is not None:
            return self._sign
        sign = ""
        if re.match("(.+)login=cvs&sign=([^&]*)", self.url):
            sign = re.match("(.+)login=cvs&sign=([^&]*)", self.url)[2]
            sign = f"login=cvs&sign={sign}"
        self._sign = sign
        return self._sign


def init(url: str = "", config: Config = None) -> Izneo:
    return Izneo(url, config)
