# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from izneo_get.config import Config
from izneo_get.config_from_file import get_config_from_file


def test_get_config_from_file():
    get_config_from_file("tests/test_config_from_file.ini")
