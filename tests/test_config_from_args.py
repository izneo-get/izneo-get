# -*- coding: utf-8 -*-
import copy
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from izneo_get.config import Config, ImageFormat, OutputFormat
from izneo_get.config_from_args import get_args
from izneo_get.action import Action

EMPTY_CONFIG = Config(
    output_folder=None,
    output_filename=None,
    image_format=None,
    image_quality=None,
    output_format=None,
    pause_sec=None,
    user_agent=None,
    continue_from_existing=None,
    authentication_from_cache=None,
)

DEFAULT_ACTION = Action.from_str("")


def test_get_args_empty(monkeypatch):
    args = ["izneo_get.py"]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == DEFAULT_ACTION
    assert url is None
    assert config_file is None
    assert config == EMPTY_CONFIG


def test_get_args_only_url(monkeypatch):
    args = ["izneo_get.py", "URL"]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == DEFAULT_ACTION
    assert url == "URL"
    assert config_file is None
    assert config == EMPTY_CONFIG


def test_get_args_only_action(monkeypatch):
    args = ["izneo_get.py", "INFOS"]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == Action.INFOS
    assert url is None
    assert config_file is None
    assert config == EMPTY_CONFIG


def test_get_args_action_and_url(monkeypatch):
    args = ["izneo_get.py", "INFOS", "URL"]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == Action.INFOS
    assert url == "URL"
    assert config_file is None
    assert config == EMPTY_CONFIG


def test_get_args_config_file(monkeypatch):
    args = ["izneo_get.py", "--config", "CONFIG_FILE"]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == DEFAULT_ACTION
    assert url is None
    assert config_file == "CONFIG_FILE"
    assert config == EMPTY_CONFIG


def test_get_args_output_folder(monkeypatch):
    args = ["izneo_get.py", "--output-folder", "OUTPUT_FOLDER"]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == DEFAULT_ACTION
    assert url is None
    assert config_file is None
    assert config.output_folder == "OUTPUT_FOLDER"
    expected_config = copy.deepcopy(EMPTY_CONFIG)
    expected_config.output_folder = "OUTPUT_FOLDER"
    assert config == expected_config


def test_get_args_output_filename(monkeypatch):
    args = ["izneo_get.py", "--output-filename", "OUTPUT_FILENAME"]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == DEFAULT_ACTION
    assert url is None
    assert config_file is None
    assert config.output_filename == "OUTPUT_FILENAME"
    expected_config = copy.deepcopy(EMPTY_CONFIG)
    expected_config.output_filename = "OUTPUT_FILENAME"
    assert config == expected_config


def test_get_args_image_format(monkeypatch):
    for arg_value, value in {
        "webp": ImageFormat.WEBP,
        "jpeg": ImageFormat.JPEG,
        "origin": ImageFormat.ORIGIN,
    }.items():
        args = ["izneo_get.py", "--image-format", arg_value]
        monkeypatch.setattr("sys.argv", args)
        config, action, url, config_file = get_args()
        assert action == DEFAULT_ACTION
        assert url is None
        assert config_file is None
        assert config.image_format == value
        expected_config = copy.deepcopy(EMPTY_CONFIG)
        expected_config.image_format = value
        assert config == expected_config


def test_get_args_image_quality(monkeypatch):
    value = 42
    args = ["izneo_get.py", "--image-quality", str(value)]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == DEFAULT_ACTION
    assert url is None
    assert config_file is None
    assert config.image_quality == value
    expected_config = copy.deepcopy(EMPTY_CONFIG)
    expected_config.image_quality = value
    assert config == expected_config


def test_get_args_output_format(monkeypatch):
    for arg_value, value in {
        "images": OutputFormat.IMAGES,
        "cbz": OutputFormat.CBZ,
        "both": OutputFormat.BOTH,
    }.items():
        args = ["izneo_get.py", "--output-format", arg_value]
        monkeypatch.setattr("sys.argv", args)
        config, action, url, config_file = get_args()
        assert action == DEFAULT_ACTION
        assert url is None
        assert config_file is None
        assert config.output_format == value
        expected_config = copy.deepcopy(EMPTY_CONFIG)
        expected_config.output_format = value
        assert config == expected_config


def test_get_args_pause(monkeypatch):
    value = 42
    args = ["izneo_get.py", "--pause", str(value)]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == DEFAULT_ACTION
    assert url is None
    assert config_file is None
    assert config.pause_sec == value
    expected_config = copy.deepcopy(EMPTY_CONFIG)
    expected_config.pause_sec = value
    assert config == expected_config


def test_get_args_user_agent(monkeypatch):
    value = "USER_AGENT"
    args = ["izneo_get.py", "--user-agent", value]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == DEFAULT_ACTION
    assert url is None
    assert config_file is None
    assert config.user_agent == value
    expected_config = copy.deepcopy(EMPTY_CONFIG)
    expected_config.user_agent = value
    assert config == expected_config


def test_get_args_continue_from_existing(monkeypatch):
    args = ["izneo_get.py", "--continue"]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == DEFAULT_ACTION
    assert url is None
    assert config_file is None
    assert config.continue_from_existing == True
    expected_config = copy.deepcopy(EMPTY_CONFIG)
    expected_config.continue_from_existing = True
    assert config == expected_config


def test_get_args_authentication_from_cache(monkeypatch):
    args = ["izneo_get.py", "--ignore-cache"]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == DEFAULT_ACTION
    assert url is None
    assert config_file is None
    assert config.authentication_from_cache == False
    expected_config = copy.deepcopy(EMPTY_CONFIG)
    expected_config.authentication_from_cache = False
    assert config == expected_config


def test_get_args_multiple(monkeypatch):
    args = [
        "izneo_get.py",
        "URL",
        "--config",
        "CONFIG_FILE",
        "--output-folder",
        "OUTPUT_FOLDER",
        "--output-filename",
        "OUTPUT_FILENAME",
        "--image-format",
        "webp",
        "--image-quality",
        "42",
        "--output-format",
        "images",
        "--pause",
        "42",
        "--user-agent",
        "USER_AGENT",
        "--continue",
        "--ignore-cache",
    ]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == DEFAULT_ACTION
    assert url == "URL"
    assert config_file == "CONFIG_FILE"
    assert config.output_folder == "OUTPUT_FOLDER"
    assert config.output_filename == "OUTPUT_FILENAME"
    assert config.image_format == ImageFormat.WEBP
    assert config.image_quality == 42
    assert config.output_format == OutputFormat.IMAGES
    assert config.pause_sec == 42
    assert config.user_agent == "USER_AGENT"
    assert config.continue_from_existing == True
    assert config.authentication_from_cache == False
    expected_config = copy.deepcopy(EMPTY_CONFIG)
    expected_config.output_folder = "OUTPUT_FOLDER"
    expected_config.output_filename = "OUTPUT_FILENAME"
    expected_config.image_format = ImageFormat.WEBP
    expected_config.image_quality = 42
    expected_config.output_format = OutputFormat.IMAGES
    expected_config.pause_sec = 42
    expected_config.user_agent = "USER_AGENT"
    expected_config.continue_from_existing = True
    expected_config.authentication_from_cache = False
    assert config == expected_config


def test_get_args_multiple_with_action(monkeypatch):
    args = [
        "izneo_get.py",
        "DOWNLOAD",
        "URL",
        "--config",
        "CONFIG_FILE",
        "--output-folder",
        "OUTPUT_FOLDER",
        "--output-filename",
        "OUTPUT_FILENAME",
        "--image-format",
        "webp",
        "--image-quality",
        "42",
        "--output-format",
        "images",
        "--pause",
        "42",
        "--user-agent",
        "USER_AGENT",
        "--continue",
        "--ignore-cache",
    ]
    monkeypatch.setattr("sys.argv", args)
    config, action, url, config_file = get_args()
    assert action == Action.DOWNLOAD
    assert url == "URL"
    assert config_file == "CONFIG_FILE"
    assert config.output_folder == "OUTPUT_FOLDER"
    assert config.output_filename == "OUTPUT_FILENAME"
    assert config.image_format == ImageFormat.WEBP
    assert config.image_quality == 42
    assert config.output_format == OutputFormat.IMAGES
    assert config.pause_sec == 42
    assert config.user_agent == "USER_AGENT"
    assert config.continue_from_existing == True
    assert config.authentication_from_cache == False
    expected_config = copy.deepcopy(EMPTY_CONFIG)
    expected_config.output_folder = "OUTPUT_FOLDER"
    expected_config.output_filename = "OUTPUT_FILENAME"
    expected_config.image_format = ImageFormat.WEBP
    expected_config.image_quality = 42
    expected_config.output_format = OutputFormat.IMAGES
    expected_config.pause_sec = 42
    expected_config.user_agent = "USER_AGENT"
    expected_config.continue_from_existing = True
    expected_config.authentication_from_cache = False
    assert config == expected_config


if __name__ == "__main__":
    ...
