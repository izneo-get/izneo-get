# -*- coding: utf-8 -*-

import asyncio
import glob
import html
import io
import os
import random
import re
import shutil
import string
import cv2
import inquirer
import numpy as np
from tqdm.asyncio import tqdm
from urllib3.util import Retry
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from PIL import Image
from typing import Any, Dict, List, Optional, Set

from izneo_get.config import ImageFormat
from .book_infos import BookInfos

BAR_FORMAT = "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"  # Progress bar format


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


def clean_attribute(attribute: str) -> str:
    if not attribute:
        return ""
    attribute = html.unescape(attribute)
    attribute = clean_name(attribute)
    return attribute


def requests_retry_session(
    retries: int = 3,
    backoff_factor: int = 1,
    status_forcelist: Optional[Set[int]] = None,
    session: Optional[Session] = None,
) -> Session:
    """Permet de gérer les cas simples de problèmes de connexions."""
    if status_forcelist is None:
        status_forcelist = {500, 502, 504}
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


def http_get(
    url: str, session: Optional[Session] = None, headers: Optional[Dict[str, str]] = None, **kwargs: Optional[Any]
) -> requests.Response:
    cookies = session.cookies if session else None
    return requests_retry_session(session=session).get(
        url, cookies=cookies, allow_redirects=True, headers=headers, **kwargs
    )


def http_post(
    url: str, session: Optional[Session] = None, headers: Optional[Dict[str, str]] = None, **kwargs: Optional[Any]
) -> requests.Response:
    cookies = session.cookies if session else None
    return requests_retry_session(session=session).post(
        url, cookies=cookies, allow_redirects=True, headers=headers, **kwargs
    )


async def async_http_get(
    url: str, session: Optional[Session] = None, headers: Optional[Dict[str, str]] = None, **kwargs: Optional[Any]
) -> requests.Response:
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
    return image.format.lower() if image.format else ""


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
    shutil.make_archive(re.sub(".zip$", "", zip_filepath, flags=re.IGNORECASE), "zip", source_folder)
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


def convert_image(input_path: str, store_path_converted: str, format: str, image_quality: int = 100) -> str:
    im = Image.open(input_path)
    im.save(store_path_converted, format, quality=image_quality)
    os.remove(input_path)
    return store_path_converted


def convert_image_if_needed(
    from_path: str, to_path: str, image_format: ImageFormat, image_quality: Optional[int] = None
) -> str:
    if not image_quality:
        image_quality = 100
    if image_format == ImageFormat.WEBP:
        return convert_image(from_path, to_path, "webp", image_quality)
    if image_format == ImageFormat.JPEG:
        return convert_image(from_path, to_path, "jpeg", image_quality)
    if image_format == ImageFormat.ORIGIN and os.path.exists(to_path) and from_path != to_path:
        os.remove(to_path)
    if from_path != to_path:
        os.rename(from_path, to_path)
    return to_path


def convert_images_in_folder(
    folder: str, image_format: ImageFormat, quality: Optional[int] = None, crop: Optional[bool] = None
) -> List[str]:
    """Convert images of a folder in a specitic format."""
    if quality is None:
        quality = 100
    if crop is None:
        crop = False
    print(f"Convert images in {image_format.value} (quality: {quality})")
    if image_format not in (ImageFormat.JPEG, ImageFormat.WEBP):
        print("Nothing to convert")
        return []
    all_files = []
    for ext in ("jpg", "jpeg", "png", "webp", "bmp"):
        all_files.extend(glob.glob(os.path.join(glob.escape(folder), f"*.{ext}"), recursive=True))
    files_converted = asyncio.run(async_convert_images(all_files, image_format, quality, crop))
    print(f"{len(files_converted)} images converted")
    return files_converted


async def async_convert_images(
    all_files: List[str], image_format: ImageFormat, quality: int = 100, crop: bool = False
) -> List[str]:
    return await tqdm.gather(
        *[async_convert_image(filename, image_format, quality, crop) for filename in all_files],
        desc="Convert images",
        bar_format=BAR_FORMAT,
    )


async def async_convert_image(filename: str, image_format: ImageFormat, quality: int = 100, crop: bool = False) -> str:
    new_filename = f"{os.path.splitext(filename)[0]}.{str(image_format.value).lower()}"
    return await asyncio.to_thread(save_image_from_path, filename, new_filename, image_format, quality, crop)


def save_image_from_path(
    filename: str, new_filename: str, image_format: ImageFormat, quality: int = 100, crop: bool = False
) -> str:
    img = auto_crop(filename) if crop else cv2.imdecode(np.fromfile(filename, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    save_image(img, new_filename, image_format, quality)
    if new_filename != filename:
        os.remove(filename)
    return new_filename


def save_image(img: np.ndarray, output_path: str, image_format: ImageFormat = ImageFormat.JPEG, quality=100) -> str:
    """
    Save image in the desired quality.

    Parameters
    ----------
    img : numpy.ndarray
        cv2 image object to display.
    output_path : str
        File path to saved image.
    image_format : ImageFormat (default ImageFormat.JPEG)
    quality : int (default 100)
        Save quality factor. Max 100 (best quality).

    Returns
    -------
    str
        Output path of saved image.
    """
    ext = output_path.split(".")[-1].lower()
    params = []
    if image_format == ImageFormat.JPEG:
        params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    if image_format == ImageFormat.WEBP:
        params = [cv2.IMWRITE_WEBP_QUALITY, quality]

    _, im_buf_arr = cv2.imencode(f".{ext}", img, params)
    im_buf_arr.tofile(output_path)
    return output_path


def auto_crop(filename: str) -> np.ndarray:
    # TODO : implement crop
    return cv2.imdecode(np.fromfile(filename, dtype=np.uint8), cv2.IMREAD_UNCHANGED)


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
    answer: Dict[str, bool] = inquirer.prompt(questions)
    return answer["answer"]


def generate_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))
