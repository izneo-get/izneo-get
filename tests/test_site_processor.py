# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from izneo_get.plugins.site_processor import SiteProcessor
from izneo_get.book_infos import BookInfos


def test_get_default_title():
    processor = SiteProcessor("")
    book_infos = BookInfos(title="title", pages=1, subtitle="", volume="")
    assert processor.get_default_title(book_infos) == "title"
    book_infos = BookInfos(title="title", pages=1, subtitle="subtitle", volume="")
    assert processor.get_default_title(book_infos) == "title - subtitle"
    book_infos = BookInfos(title="title", pages=1, subtitle="subtitle", volume="1")
    assert processor.get_default_title(book_infos) == "title - 01. subtitle"
    book_infos = BookInfos(title="title", pages=1, subtitle="subtitle", volume="1234")
    assert processor.get_default_title(book_infos) == "title - 1234. subtitle"


if __name__ == "__main__":
    ...
