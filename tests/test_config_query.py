# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from izneo_get.config import Config
from izneo_get.config_from_query import ConfigQuery, digit_validation
import inquirer


def test_digit_validation():
    assert digit_validation(None, "") == True
    assert digit_validation(None, "42") == True
    assert digit_validation(None, "ABC") == False


def test_update_item_output_folder(monkeypatch):
    config = Config()
    config_query = ConfigQuery(config)

    monkeypatch.setattr(inquirer, "prompt", lambda _: {"value": "TEST"})
    config_query.update_item_output_folder()
    assert config.output_folder == "TEST"


def test_update_item_filename_pattern(monkeypatch):
    config = Config()
    config_query = ConfigQuery(config)

    monkeypatch.setattr(inquirer, "prompt", lambda _: {"value": "TEST"})
    config_query.update_item_filename_pattern()
    assert config.output_filename == "TEST"
    monkeypatch.setattr(inquirer, "prompt", lambda _: {"value": ""})
    config_query.update_item_filename_pattern()
    assert config.output_filename == "TEST"


def test_update_item_image_format(monkeypatch):
    config = Config()
    config_query = ConfigQuery(config)

    monkeypatch.setattr(inquirer, "prompt", lambda _: {"image_format": "JPEG"})
    config_query.update_item_image_format()
    assert config.image_format == "JPEG"
    monkeypatch.setattr(inquirer, "prompt", lambda _: {"image_format": ""})
    config_query.update_item_image_format()
    assert config.image_format == "JPEG"


def test_update_item_image_quality(monkeypatch):
    config = Config()
    config_query = ConfigQuery(config)

    monkeypatch.setattr(inquirer, "prompt", lambda _: {"value": "42"})
    config_query.update_item_image_quality()
    assert config.image_quality == 42
    monkeypatch.setattr(inquirer, "prompt", lambda _: {"value": ""})
    config_query.update_item_image_quality()
    assert config.image_quality == 42


def test_update_item_output_format(monkeypatch):
    config = Config()
    config_query = ConfigQuery(config)

    monkeypatch.setattr(inquirer, "prompt", lambda _: {"output_format": "IMAGES"})
    config_query.update_item_output_format()
    assert config.output_format == "IMAGES"
    monkeypatch.setattr(inquirer, "prompt", lambda _: {"output_format": ""})
    config_query.update_item_output_format()
    assert config.output_format == "IMAGES"


def test_update_item_pause_sec(monkeypatch):
    config = Config()
    config_query = ConfigQuery(config)

    monkeypatch.setattr(inquirer, "prompt", lambda _: {"value": "42"})
    config_query.update_item_pause_sec()
    assert config.pause_sec == 42
    monkeypatch.setattr(inquirer, "prompt", lambda _: {"value": ""})
    config_query.update_item_pause_sec()
    assert config.pause_sec == 42


def test_update_item_user_agent(monkeypatch):
    config = Config()
    config_query = ConfigQuery(config)

    monkeypatch.setattr(inquirer, "prompt", lambda _: {"value": "TEST"})
    config_query.update_item_user_agent()
    assert config.user_agent == "TEST"
    monkeypatch.setattr(inquirer, "prompt", lambda _: {"value": ""})
    config_query.update_item_user_agent()
    assert config.user_agent == "TEST"


def test_update_item_continue_from_existing(monkeypatch):
    config = Config()
    config_query = ConfigQuery(config)

    monkeypatch.setattr(inquirer, "prompt", lambda _: {"continue_from_existing": True})
    config_query.update_item_continue_from_existing()
    assert config.continue_from_existing == True
    monkeypatch.setattr(inquirer, "prompt", lambda _: {"continue_from_existing": False})
    config_query.update_item_continue_from_existing()
    assert config.continue_from_existing == False
