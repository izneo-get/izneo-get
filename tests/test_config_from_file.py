# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from izneo_get.config import Config, ImageFormat, OutputFormat
from izneo_get.config_from_file import get_config_from_file


def compare_with_args(config_file: str):
    default_config = Config()
    args_config = Config(
        output_folder="OUTPUT_FOLDER_FROM_ARGS",
        output_filename="OUTPUT_FILENAME_FROM_ARGS",
        image_format=ImageFormat.WEBP,
        image_quality=21,
        output_format=OutputFormat.CBZ,
        pause_sec=84,
        user_agent="USER_AGENT_FROM_ARGS",
        continue_from_existing=not default_config.continue_from_existing,
        authentication_from_cache=not default_config.authentication_from_cache,
    )
    config: Config = get_config_from_file(config_file, args_config)
    assert config == args_config


def test_get_config_from_file_empty():
    default_config = Config()
    config_file = "tests/resources/config_empty.ini"
    config: Config = get_config_from_file(config_file)
    assert config == default_config

    compare_with_args(config_file)


def test_get_config_from_file_missing():
    config_file = "tests/resources/config_missing_values.ini"
    config: Config = get_config_from_file(config_file)
    default_config = Config()
    assert config.output_folder == "THIS_IS_MY_OUTPUT_FOLDER"
    assert config.user_agent == "THIS_IS_MY_USER_AGENT"
    assert config.pause_sec == 42
    assert config.continue_from_existing == False
    assert config.output_filename == default_config.output_filename
    assert config.image_format == default_config.image_format
    assert config.image_quality == default_config.image_quality
    assert config.output_format == default_config.output_format
    assert config.authentication_from_cache == default_config.authentication_from_cache
    assert config.cache_folder == default_config.cache_folder

    compare_with_args(config_file)


def test_get_config_from_file_full():
    config_file = "tests/resources/config_full.ini"
    config: Config = get_config_from_file(config_file)
    assert config.output_folder == "THIS_IS_MY_OUTPUT_FOLDER"
    assert config.output_filename == "THIS_IS_MY_OUTPUT_FILENAME"
    assert config.image_format == ImageFormat.WEBP
    assert config.image_quality == 42
    assert config.output_format == OutputFormat.CBZ
    assert config.pause_sec == 24
    assert config.user_agent == "THIS_IS_MY_USER_AGENT"
    assert config.continue_from_existing == True
    assert config.authentication_from_cache == False

    compare_with_args(config_file)


if __name__ == "__main__":
    test_get_config_from_file_empty()
