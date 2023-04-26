import os
from context import tools
import pytest
import re
from context import book_infos


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
    if os.path.exists("tests/test.txt"):
        os.remove("tests/test.txt")
    for i in range(1, 8):
        if os.path.exists(f"tests/test ({i}).txt"):
            os.remove(f"tests/test ({i}).txt")

    assert tools.get_unique_name("tests/test.txt") == "tests/test.txt"
    with open("tests/test.txt", "w") as f:
        f.write("test")
    assert tools.get_unique_name("tests/test.txt") == "tests/test (1).txt"
    with open("tests/test (1).txt", "w") as f:
        f.write("test")
    assert tools.get_unique_name("tests/test.txt") == "tests/test (2).txt"
