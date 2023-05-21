import asyncio
import os
import shutil
import cv2

import inquirer
import numpy as np
from context import tools
import pytest
import re
from context import book_infos
from izneo_get.config import ImageFormat


def clean_output(output_path):
    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    os.makedirs(output_path, exist_ok=True)


def test_strip_tags():
    assert tools.strip_tags("<p>Hello, <b>world!</b></p>") == "Hello, world!"
    assert tools.strip_tags("<h1>Title</h1><p>Paragraph</p>") == "TitleParagraph"
    assert tools.strip_tags("<a href='https://example.com'>Link</a>") == "Link"
    assert tools.strip_tags("No tags") == "No tags"


def test_clean_name():
    assert tools.clean_name("test_file.txt") == "test_file.txt"
    assert tools.clean_name("test<file>.txt") == "test_file_.txt"
    assert tools.clean_name("test/file.txt") == "test_file.txt"
    assert tools.clean_name("test\\file.txt") == "test_file.txt"
    assert tools.clean_name("test:*file.txt") == "test__file.txt"
    assert tools.clean_name("test?file.txt") == "test_file.txt"
    assert tools.clean_name("test|file.txt") == "test_file.txt"
    assert tools.clean_name("test  file.txt") == "test file.txt"
    assert tools.clean_name("test   file.txt") == "test file.txt"
    assert tools.clean_name("test   file...") == "test file"
    assert tools.clean_name("   test file...   ") == "test file"
    assert tools.clean_name("test<serie>\\file.txt", directory=True) == "test_serie_\\file.txt"


def test_requests_retry_session():
    session = tools.requests_retry_session()
    assert session is not None
    response = tools.requests_retry_session(session=session, retries=1, status_forcelist=[]).get(
        url="https://httpstat.us/500"
    )
    assert response.status_code == 500
    with pytest.raises(tools.requests.exceptions.RetryError):
        tools.requests_retry_session(session=session, retries=1, status_forcelist=[500]).get(
            url="https://httpstat.us/500"
        )
    response = tools.requests_retry_session(session=session).get(url="https://httpstat.us/200")
    assert response.status_code == 200


def test_http_get():
    response = tools.http_get("https://httpstat.us/200")
    assert response.status_code == 200
    response = tools.http_get("https://httpstat.us/401")
    assert response.status_code == 401
    with pytest.raises(tools.requests.exceptions.RetryError):
        tools.http_get("https://httpstat.us/500")


def test_async_http_get():
    response = asyncio.run(tools.async_http_get("https://httpstat.us/200"))
    assert response.status_code == 200


def test_clean_attribute():
    attribute = '&lt;p class="example"&gt;'
    cleaned_attribute = tools.clean_attribute(attribute)
    assert cleaned_attribute == "_p class=_example__"


def test_check_version():
    version = tools.check_version("0.0.0")
    assert re.match(r"(\d+)\.(\d+)\.(\d+)", version)


def test_get_image_type():
    with open("tests/resources/image.png", "rb") as f:
        assert tools.get_image_type(f.read()) == "png"
    with open("tests/resources/image.jpeg", "rb") as f:
        assert tools.get_image_type(f.read()) == "jpeg"
    with open("tests/resources/image.webp", "rb") as f:
        assert tools.get_image_type(f.read()) == "webp"


def test_get_name_from_pattern():
    infos = book_infos.BookInfos("Title", 1)
    infos.title = "Title"
    infos.serie = "Serie"
    infos.volume = "Volume"
    infos.authors = "Author"
    pattern = "{title} - {serie} - {volume} - {authors}"
    assert tools.get_name_from_pattern(pattern, infos) == "Title - Serie - Volume - Author"

    infos.volume = "1"
    infos.chapter = "2"
    pattern = "{title} - {serie} - {volume:2} - {chapter:2}"
    assert tools.get_name_from_pattern(pattern, infos) == "Title - Serie - 01 - 02"

    pattern = "{title} - {serie} - {volume:3} - {chapter:3}"
    assert tools.get_name_from_pattern(pattern, infos) == "Title - Serie - 001 - 002"

    infos.volume = "Volume"
    assert tools.get_name_from_pattern(pattern, infos) == "Title - Serie - Volume - 002"


def test_get_unique_name():
    clean_test_files()
    assert tools.get_unique_name("tests/test.txt") == "tests/test.txt"
    with open("tests/test.txt", "w") as f:
        f.write("test")
    assert tools.get_unique_name("tests/test.txt") == "tests/test (1).txt"
    with open("tests/test (1).txt", "w") as f:
        f.write("test")
    assert tools.get_unique_name("tests/test.txt") == "tests/test (2).txt"
    clean_test_files()


def clean_test_files():
    for file in {
        "tests/test.txt",
        "tests/resources.cbz",
        "tests/to_convert.jpeg",
        "tests/to_convert.jpg",
        "tests/to_convert.webp",
    }:
        if os.path.exists(file):
            os.remove(file)
    for i in range(1, 8):
        if os.path.exists(f"tests/test ({i}).txt"):
            os.remove(f"tests/test ({i}).txt")


def test_create_cbz():
    clean_test_files()
    expected_path = "tests/resources.cbz"
    cbz_path = tools.create_cbz("tests/resources")
    assert cbz_path == expected_path
    assert os.path.exists(cbz_path)
    assert os.path.getsize(cbz_path) > 0
    clean_test_files()


def test_convert_image():
    convert_from = "tests/to_convert.jpg"
    for format in ["jpeg", "webp"]:
        shutil.copyfile("tests/resources/image.jpeg", convert_from)
        convert_to = f"tests/to_convert.{format}"
        if os.path.exists(convert_to):
            os.remove(convert_to)
        ret = tools.convert_image(convert_from, convert_to, format, 100)
        assert ret == convert_to
        assert os.path.exists(convert_to)
        assert os.path.getsize(convert_to) > 0
        os.remove(convert_to)


def test_convert_image_if_needed():
    convert_from = "tests/to_convert.tmp"
    for ext, format in [("jpeg", ImageFormat.JPEG), ("webp", ImageFormat.WEBP), ("jpeg", ImageFormat.ORIGIN)]:
        shutil.copyfile("tests/resources/image.jpeg", convert_from)
        convert_to = f"tests/to_convert.{ext}"
        if os.path.exists(convert_to):
            os.remove(convert_to)
        ret = tools.convert_image_if_needed(convert_from, convert_to, format, 100)
        assert ret == convert_to
        assert os.path.exists(convert_to)
        assert os.path.getsize(convert_to) > 0
        assert not os.path.exists(convert_from)
        os.remove(convert_to)

    convert_from = convert_to = "tests/to_convert.jpeg"
    shutil.copyfile("tests/resources/image.jpeg", convert_from)
    file_size = os.path.getsize(convert_from)
    ret = tools.convert_image_if_needed(convert_from, convert_to, ImageFormat.ORIGIN, 1)
    assert ret == convert_to
    assert os.path.exists(convert_to)
    assert os.path.getsize(convert_to) == file_size
    os.remove(convert_to)


def test_question_yes_no(monkeypatch):
    monkeypatch.setattr(inquirer, "prompt", lambda _: {"answer": True})
    assert tools.question_yes_no("question") == True


def test_save_image():
    for source in ["tests/resources/image.jpeg", "tests/resources/image.png", "tests/resources/image.webp"]:
        img = cv2.imdecode(np.fromfile(source, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        for format in [ImageFormat.JPEG, ImageFormat.WEBP]:
            convert_to = f"tests/to_convert.{str(format.value).lower()}"
            if os.path.exists(convert_to):
                os.remove(convert_to)
            ret = tools.save_image(img, convert_to, format, 10)
            assert ret == convert_to
            assert os.path.exists(convert_to)
            assert os.path.getsize(convert_to) > 0
            os.remove(convert_to)


def test_convert_images_in_folder():
    output_path = "tests/output"
    clean_output(output_path)
    for i in range(4):
        shutil.copyfile("tests/resources/image.jpeg", f"tests/output/to_convert_{i}.jpeg")

    for format in [ImageFormat.JPEG, ImageFormat.WEBP]:
        assert tools.convert_images_in_folder("tests/output", format, 10)
        for i in range(4):
            assert os.path.exists(f"tests/output/to_convert_{i}.{format.value.lower()}")
    assert not tools.convert_images_in_folder("tests/output", ImageFormat.ORIGIN, 10)
    clean_output(output_path)


if __name__ == "__main__":
    ...
