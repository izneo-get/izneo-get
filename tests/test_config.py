# -*- coding: utf-8 -*-
import copy
import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from izneo_get.config import Config, ImageFormat, OutputFormat
from izneo_get.config_from_file import get_config_from_file


def test_to_dict():
    config = Config()
    config_dict = config.to_dict()
    assert config_dict["output_folder"] == config.output_folder
    assert config_dict["output_filename"] == config.output_filename
    assert config_dict["image_format"] == config.image_format.value
    assert config_dict["image_quality"] == str(config.image_quality)
    assert config_dict["output_format"] == config.output_format.value
    assert config_dict["pause_sec"] == str(config.pause_sec)
    assert config_dict["user_agent"] == config.user_agent
    assert config_dict["continue_from_existing"] == str(config.continue_from_existing)
    assert config_dict["authentication_from_cache"] == str(config.authentication_from_cache)


def test_save_config():
    config_file = "tests/temp.cfg"
    default_config = Config()
    config = Config(
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
    if os.path.exists(config_file):
        os.remove(config_file)
    config.save_config(config_file)
    assert os.path.exists(config_file)

    config_read = get_config_from_file(config_file)
    assert config == config_read


if __name__ == "__main__":
    test_save_config()
