# -*- coding: utf-8 -*-
__version__ = "1.0.0"
"""
Source : https://github.com/izneo-get/izneo-get

Ce script permet de récupérer une BD présente sur https://www.izneo.com/fr/ dans la limite des capacités de notre compte existant.

"""
import importlib
import re
import os
import sys
import shutil
from typing import List, Optional, Tuple
from .config_from_args import get_args
from .tools import check_version, convert_images_in_folder, create_cbz
from .plugins.site_processor import SiteProcessor
from .config import Config, ImageFormat, OutputFormat
from .config_from_query import ConfigQuery
from .config_from_file import get_config_from_file

# from .plugins.izneo import Izneo  # Force import for PyInstaller

CONFIG_FILE = "izneo_get.cfg"


def get_config(args_config: Config, config_file: Optional[str]) -> Config:
    if config_file:
        if not os.path.exists(config_file):
            print(f'Configuration file "{config_file}" doesn\'t exist.')
            sys.exit(1)
        return get_config_from_file(config_file, args_config)
    return get_config_from_file(CONFIG_FILE if os.path.exists(CONFIG_FILE) else "", args_config)


def main() -> None:
    check_version(__version__)

    args_config, url, config_file = get_args()
    config = get_config(args_config, config_file)
    if not url:
        config_query = ConfigQuery(config, CONFIG_FILE)
        config = config_query.update_config_by_command()

    while not url:
        url = input("URL: ")

    # List of all URLs to process.
    url_list = get_all_urls(url)

    for url, forced_title in url_list:
        processor = get_site_processor(url=url, config=config)
        if not processor:
            continue
        processor.authenticate()
        infos = processor.get_book_infos()
        print(infos)
        save_path = processor.download(forced_title)
        if not save_path:
            print("WARNING: Nothing was downloaded.")
            return
        # print("Download completed")

        if config.image_format and config.image_format != ImageFormat.ORIGIN:
            convert_images_in_folder(save_path, config.image_format, config.image_quality)

        # If needed, we create an archive.
        if config.output_format in [OutputFormat.CBZ, OutputFormat.BOTH]:
            expected_cbz_name = save_path.strip(".cbz") + ".cbz"
            if config.continue_from_existing and os.path.exists(expected_cbz_name):
                print(f'File "{expected_cbz_name}" already exists.')
            else:
                create_cbz(save_path)

        # If.
        if config.output_format == OutputFormat.CBZ:
            shutil.rmtree(save_path.strip(".cbz"))

    print("Done!")


def get_all_urls(url: str) -> List[Tuple[str, str]]:
    return get_urls_from_file(url) if os.path.exists(url) else [(url, "")]


def get_urls_from_file(url: str, encoding: str = "utf-8") -> List[tuple[str, str]]:
    url_list: List[tuple[str, str]] = []
    with open(url, "r", encoding=encoding) as f:
        lines = f.readlines()
    next_forced_title = ""
    for line in lines:
        line = line.strip()
        # On cherche si on a un titre forcé.
        res = ""
        if line and line[0] == "#":
            res = re.findall(r"--force-title (.+)", line)
            res = res[0].strip() if res else ""
        if res:
            next_forced_title = res
        if line and line[0] != "#":
            url_list.append((line, next_forced_title))
            next_forced_title = ""
    return url_list


def get_site_processor(url: str, config: Config) -> Optional[SiteProcessor]:
    parser = None
    # Load all modules in the plugin directory.
    for module in os.listdir(f"{os.path.dirname(__file__)}/plugins"):
        if module == "__init__.py" or module[-3:] != ".py":
            continue
        module = importlib.import_module(f"izneo_get.plugins.{module[:-3]}")
        parser = module.init(url, config)
        if parser.is_valid_url(url):
            return parser
        parser = None
    return parser


if __name__ == "__main__":
    main()
