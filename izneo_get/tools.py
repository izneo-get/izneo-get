# -*- coding: utf-8 -*-

import asyncio
import html
import io
import os
import re
import shutil
import inquirer
from urllib3.util import Retry
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from PIL import Image
from typing import Dict, Set

from izneo_get.config import ImageFormat
from .book_infos import BookInfos


def strip_tags(html: str) -> str:
    """Permet de supprimer tous les tags HTML d'une chaine de caractère.

    Parameters
    ----------
    html : str
        La chaine de caractère d'entrée.

    Returns
    -------
    str
        La chaine purgée des tous les tags HTML.
    """
    return re.sub("<[^<]+?>", "", html)


def clean_name(name: str, directory: bool = False) -> str:
    """Permet de supprimer les caractères interdits dans les chemins.

    Parameters
    ----------
    name : str
        La chaine de caractère d'entrée.

    Returns
    -------
    str
        La chaine purgée des tous les caractères non désirés.
    """
    chars = ':*<>?"|'
    if not directory:
        chars += "\\/"
    for c in chars:
        name = name.replace(c, "_")
    name = re.sub(r"\s+", " ", name).strip()
    name = re.sub(r"\.+$", "", name).strip()
    return name


def clean_attribute(attribute: str):
    attribute = html.unescape(attribute)
    attribute = clean_name(attribute)
    return attribute


def requests_retry_session(
    retries: int = 3,
    backoff_factor: int = 1,
    status_forcelist: Set[int] = {500, 502, 504},
    session: Session = None,
) -> Session:
    """Permet de gérer les cas simples de problèmes de connexions."""
    session = session or Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def http_get(url: str, session: Session = None, headers: Dict = None, **kwargs) -> requests.Response:
    cookies = session.cookies if session else None
    return requests_retry_session(session=session).get(
        url, cookies=cookies, allow_redirects=True, headers=headers, **kwargs
    )


async def async_http_get(url: str, session: Session = None, headers: Dict = None, **kwargs) -> requests.Response:
    return await asyncio.to_thread(http_get, url, session, headers, **kwargs)


def check_version(version: str) -> str:
    latest_version_url = "https://raw.githubusercontent.com/izneo-get/izneo-get/master/VERSION"
    latest_version = ""
    res = requests.get(latest_version_url)
    if res.status_code != 200:
        print(f"Version {version} (impossible de vérifier la version officielle)")
    else:
        latest_version = res.text.strip()
        if latest_version == version:
            print(f"Version {version} (version officielle)")
        else:
            print(f"Version {version} (la version officielle est différente: {latest_version})")
            print("Please check https://github.com/izneo-get/izneo-get/releases/latest")
    print()
    return latest_version


def get_image_type(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    return image.format.lower()


def get_name_from_pattern(pattern: str, infos: BookInfos) -> str:
    """Permet de créer un nom de fichier à partir d'un pattern.

    Parameters
    ----------
    pattern : str
        Le pattern à utiliser.
    infos : BookInfos
        Les informations du livre.

    Returns
    -------
    str
        Le nom de fichier.
    """
    name = pattern
    for attr in infos.__dict__:
        name = name.replace("{" + attr + "}", str(getattr(infos, attr)))
    if "{volume:2}" in name:
        if infos.volume.isdigit():
            name = name.replace("{volume:2}", f"{int(infos.volume):02d}")
        else:
            name = name.replace("{volume:2}", infos.volume)
    if "{volume:3}" in name:
        if infos.volume.isdigit():
            name = name.replace("{volume:3}", f"{int(infos.volume):03d}")
        else:
            name = name.replace("{volume:3}", infos.volume)
    if "{chapter:2}" in name:
        if infos.chapter.isdigit():
            name = name.replace("{chapter:2}", f"{int(infos.chapter):02d}")
        else:
            name = name.replace("{chapter:2}", infos.chapter)
    if "{chapter:3}" in name:
        if infos.chapter.isdigit():
            name = name.replace("{chapter:3}", f"{int(infos.chapter):03d}")
        else:
            name = name.replace("{chapter:3}", infos.chapter)
    return name


def create_cbz(source_folder: str) -> str:
    print("Create CBZ...")
    zip_filepath = get_unique_name(f"{source_folder}.zip")
    shutil.make_archive(zip_filepath.strip(".zip"), "zip", source_folder)
    cbz_filepath = get_unique_name(f"{source_folder}.cbz")
    os.rename(zip_filepath, cbz_filepath)
    print(f"CBZ created: {cbz_filepath}")
    return cbz_filepath


def get_unique_name(path: str):
    """Permet de créer un nom de fichier unique.

    Parameters
    ----------
    path : str
        Le chemin du fichier.

    Returns
    -------
    str
        Le nom de fichier unique.
    """
    if not os.path.exists(path):
        return path
    path, ext = os.path.splitext(path)
    i = 1
    while os.path.exists(f"{path} ({i}){ext}"):
        i += 1
    return f"{path} ({i}){ext}"


def convert_image(store_path: str, store_path_converted: str, format: str, image_quality: int = 100) -> str:
    im = Image.open(store_path)
    im.save(store_path_converted, format, quality=image_quality)
    os.remove(store_path)
    return store_path_converted


def convert_image_if_needed(from_path: str, to_path: str, image_format: ImageFormat, image_quality: int = 100) -> str:
    if image_format == ImageFormat.WEBP:
        return convert_image(from_path, to_path, "webp", image_quality)
    if image_format == ImageFormat.JPEG:
        return convert_image(from_path, to_path, "jpeg", image_quality)
    if image_format == ImageFormat.ORIGIN and os.path.exists(to_path) and from_path != to_path:
        os.remove(to_path)
    if from_path != to_path:
        os.rename(from_path, to_path)
    return to_path


def question_yes_no(message: str, default: bool = True, carousel: bool = True) -> bool:
    questions = [
        inquirer.List(
            "answer",
            message=message,
            choices=[
                ("Yes", True),
                ("No", False),
            ],
            default=default,
            carousel=carousel,
        )
    ]
    answer = inquirer.prompt(questions)
    return answer["answer"]
