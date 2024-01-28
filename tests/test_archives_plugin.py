# -*- coding: utf-8 -*-
import asyncio
import os
import shutil
import sys
from typing import List
from izneo_get.config import OutputFormat

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from izneo_get.plugins.archives import Archives
from izneo_get.book_infos import BookInfos


def test_is_valid_url():
    processor = Archives()
    assert processor.is_valid_url("https://archive.org/details/id") == True
    assert processor.is_valid_url("https://archive.org/details/id/something/else") == True
    assert processor.is_valid_url("dummy") == False


def test_authenticate_from_email():
    processor = Archives()
    processor._authenticate_from_email("archive.org@e-courrier.eu", "plop")
    assert processor.session is not None


def test_get_book_infos():
    # url = "https://www.izneo.com/fr/bd/humour/asterix-5841/asterix-asterix-le-gaulois-n-1-4707"
    # processor = Izneo(url)
    # infos: BookInfos = processor.get_book_infos()
    # assert infos.title == "Astérix"
    # assert infos.pages == 13
    # assert infos.subtitle == "Astérix - Astérix le Gaulois - n°1"
    # assert infos.volume == "1"
    ...


def test_download_book_infos():
    # url = "https://www.izneo.com/fr/bd/humour/asterix-5841/asterix-asterix-le-gaulois-n-1-4707"
    # processor = Izneo(url)
    # # processor.__init_session("123456")
    # infos = processor._download_book_infos()
    # assert infos["title"] == "Astérix"
    # assert infos["nbPage"] == 13
    # assert infos["subtitle"] == "Astérix - Astérix le Gaulois - n°1"
    # assert infos["volume"] == "1"
    ...


def test_get_book_id():
    # url = "https://reader.izneo.com/read/1234567890"
    # processor = Izneo(url)
    # assert processor._get_book_id() == "1234567890"

    # url = "https://reader.izneo.com/read/1234567890?dummy=test"
    # processor = Izneo(url)
    # assert processor._get_book_id() == "1234567890"

    # url = "https://www.izneo.com/fr/bd/science-fiction/serie-1234/nom-de-l-album-5678"
    # processor = Izneo(url)
    # assert processor._get_book_id() == "5678"

    # url = "https://www.izneo.com/fr/bd/science-fiction/serie-1234/nom-de-l-album-5678/read?exiturl=https://www.izneo.com/fr/bd/science-fiction/serie-1234/autre-0000"
    # processor = Izneo(url)
    # assert processor._get_book_id() == "5678"
    ...


if __name__ == "__main__":
    ...
