# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from izneo_get.plugins.izneo import Izneo


def test_is_valid_url():
    processor = Izneo()
    assert processor.is_valid_url("https://reader.izneo.com/read/123456789") == True
    assert processor.is_valid_url("https://reader.izneo.com/read/123456789?exiturl=something") == True
    assert processor.is_valid_url("https://www.izneo.com/fr/bd/science-fiction/dummy-1234/dummy-56789") == True
    assert processor.is_valid_url("dummy") == False
