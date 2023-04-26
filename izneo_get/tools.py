# -*- coding: utf-8 -*-

import html
import io
import os
import re
import shutil
from urllib3.util import Retry
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from PIL import Image
from typing import Set
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
    status_forcelist: Set[int] = (500, 502, 504),
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
