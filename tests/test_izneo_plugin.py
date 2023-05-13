# -*- coding: utf-8 -*-
import asyncio
import os
import shutil
import sys
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from izneo_get.plugins.izneo import Izneo
from izneo_get.book_infos import BookInfos


def test_is_valid_url():
    processor = Izneo()
    assert processor.is_valid_url("https://reader.izneo.com/read/123456789") == True
    assert processor.is_valid_url("https://reader.izneo.com/read/123456789?exiturl=something") == True
    assert processor.is_valid_url("https://www.izneo.com/fr/bd/science-fiction/dummy-1234/dummy-56789") == True
    assert processor.is_valid_url("dummy") == False


def test_clean_url():
    processor: Izneo = Izneo()
    url = "https://reader.izneo.com/read/123456789"
    expected_url = "https://reader.izneo.com/read/123456789"
    assert processor._Izneo__clean_url(url) == expected_url

    url = "https://reader.izneo.com/read/123456789?exiturl=http%3A%2F%2Fwww.example.com%2F&test=dummy"
    expected_url = "https://reader.izneo.com/read/123456789?exiturl=http%3A%2F%2Fwww.example.com%2F&test=dummy"
    assert processor._Izneo__clean_url(url) == expected_url

    url = "https://reader.izneo.com/read/123456789?exiturl=http://www.example.com/&test=dummy"
    expected_url = "https://reader.izneo.com/read/123456789?exiturl=http%3A%2F%2Fwww.example.com%2F&test=dummy"
    assert processor._Izneo__clean_url(url) == expected_url


def test_download():
    url = "https://www.izneo.com/fr/webtoon/shojo/moi-apprentie-deesse-44901/episode-0-97863/read/1?exiturl=https://www.izneo.com/fr/webtoon/shojo/moi-apprentie-deesse-44901"
    processor = Izneo(url)
    ...


def test_async_download_page():
    output_path = "tests/output"
    clean_output(output_path)
    url = "https://www.izneo.com/fr/bd/humour/asterix-5841/asterix-asterix-le-gaulois-n-1-4707"
    processor = Izneo(url)
    # processor.__init_session("123456")
    title = "test"
    res: str = asyncio.run(processor._Izneo__async_download_page(0, title, output_path))
    assert res == "tests/output/test 001.jpeg"
    assert os.path.exists(res)
    assert os.path.isfile(res)
    assert os.path.getsize(res) > 0
    clean_output(output_path)


def test_async_download_all_pages():
    output_path = "tests/output"
    clean_output(output_path)
    url = "https://www.izneo.com/fr/bd/humour/asterix-5841/asterix-asterix-le-gaulois-n-1-4707"
    processor = Izneo(url)
    processor.get_book_infos()
    processor._Izneo__book_infos.custom_fields["pages"] = processor._Izneo__book_infos.custom_fields["pages"][:2]
    # processor.__init_session("123456")
    title = "test"
    res: str = asyncio.run(processor._Izneo__async_download_all_pages(title, output_path))
    assert len(res) == 2
    assert res[0] == "tests/output/test 001.jpeg"
    assert os.path.exists(res[0])
    assert os.path.isfile(res[0])
    assert os.path.getsize(res[0]) > 0
    clean_output(output_path)


def test_download_all_pages():
    output_path = "tests/output"
    clean_output(output_path)
    url = "https://www.izneo.com/fr/bd/humour/asterix-5841/asterix-asterix-le-gaulois-n-1-4707"
    processor = Izneo(url)
    processor.get_book_infos()
    processor._Izneo__book_infos.custom_fields["pages"] = processor._Izneo__book_infos.custom_fields["pages"][:2]
    # processor.__init_session("123456")
    title = "test"
    res: List[str] = processor._Izneo__download_all_pages(title, output_path)
    assert len(res) == 2
    assert res[0] == "tests/output/test 001.jpeg"
    assert os.path.exists(res[0])
    assert os.path.isfile(res[0])
    assert os.path.getsize(res[0]) > 0
    clean_output(output_path)


def test_uncrypt_image():
    crypted_image = "tests/resources/crypted_image.bin"
    uncrypted_image = "tests/resources/uncrypted_image.jpeg"
    key = "0t3WeNQ1HrrxJKo8qNTQQg=="
    iv = "YQqHDniN+GSVSga02sekIA=="
    with open(crypted_image, "rb") as f:
        uncrypted = Izneo.uncrypt_image(f.read(), key, iv)
        with open(uncrypted_image, "rb") as f:
            assert uncrypted == f.read()


def clean_output(output_path):
    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    os.makedirs(output_path, exist_ok=True)


def test_get_book_infos():
    url = "https://www.izneo.com/fr/bd/humour/asterix-5841/asterix-asterix-le-gaulois-n-1-4707"
    processor = Izneo(url)
    infos: BookInfos = processor.get_book_infos()
    assert infos.title == "Astérix"
    assert infos.pages == 13
    assert infos.subtitle == "Astérix - Astérix le Gaulois - n°1"
    assert infos.volume == "1"


def test_download_book_infos():
    url = "https://www.izneo.com/fr/bd/humour/asterix-5841/asterix-asterix-le-gaulois-n-1-4707"
    processor = Izneo(url)
    # processor.__init_session("123456")
    infos = processor._Izneo__download_book_infos()
    assert infos["title"] == "Astérix"
    assert infos["nbPage"] == 13
    assert infos["subtitle"] == "Astérix - Astérix le Gaulois - n°1"
    assert infos["volume"] == "1"


def test_get_book_id():
    url = "https://reader.izneo.com/read/1234567890"
    processor = Izneo(url)
    assert processor._Izneo__get_book_id() == "1234567890"

    url = "https://reader.izneo.com/read/1234567890?dummy=test"
    processor = Izneo(url)
    assert processor._Izneo__get_book_id() == "1234567890"

    url = "https://www.izneo.com/fr/bd/science-fiction/serie-1234/nom-de-l-album-5678"
    processor = Izneo(url)
    assert processor._Izneo__get_book_id() == "5678"

    url = "https://www.izneo.com/fr/bd/science-fiction/serie-1234/nom-de-l-album-5678/read?exiturl=https://www.izneo.com/fr/bd/science-fiction/serie-1234/autre-0000"
    processor = Izneo(url)
    assert processor._Izneo__get_book_id() == "5678"


def test_get_signature():
    url = "https://reader.izneo.com/read/1234567890"
    processor = Izneo(url)
    assert processor._Izneo__get_signature() == ""

    url = "https://reader.izneo.com/read/1234567890?exiturl=https%3A%2F%2Fdummy.source.fr%2F%3Fln%3Dalbum%26docid%3D1234&login=cvs&sign=1234567890AZERTYUIOP"
    processor = Izneo(url)
    assert processor._Izneo__get_signature() == "login=cvs&sign=1234567890AZERTYUIOP"


if __name__ == "__main__":
    test_download_all_pages()
