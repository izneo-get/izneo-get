# -*- coding: utf-8 -*-
__version__ = "1.00.00"
"""
Source : https://github.com/izneo-get/izneo-get

Ce script permet de récupérer une BD présente sur https://www.izneo.com/fr/ dans la limite des capacités de notre compte existant.

usage: izneo_get.py [-h] [--session-id SESSION_ID] 
                    [--output-folder OUTPUT_FOLDER]
                    [--output-format {jpg,both,cbz}] [--config CONFIG]
                    [--from-page FROM_PAGE] [--limit LIMIT] [--pause PAUSE]
                    [--full-only] [--continue] [--user-agent USER_AGENT]
                    [--webp WEBP] [--tree] [--force-title FORCE_TITLE]
                    [--encoding ENCODING]
                    url

Script pour sauvegarder une BD Izneo.

positional arguments:
  url                   L'URL de la BD à récupérer ou le chemin vers un
                        fichier local contenant une liste d'URLs

optional arguments:
  -h, --help            show this help message and exit
  --session-id SESSION_ID, -s SESSION_ID
                        L'identifiant de session
  --output-folder OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        Répertoire racine de téléchargement
  --output-format {jpg,both,cbz}, -f {jpg,both,cbz}
                        Répertoire racine de téléchargement
  --config CONFIG       Fichier de configuration
  --from-page FROM_PAGE
                        Première page à récupérer (défaut : 0)
  --limit LIMIT         Nombre de pages à récupérer au maximum (défaut : 1000)
  --pause PAUSE         Pause (en secondes) à respecter après chaque
                        téléchargement d'image
  --full-only           Ne prend que les liens de BD disponible dans
                        l'abonnement
  --continue            Pour reprendre là où on en était
  --user-agent USER_AGENT
                        User agent à utiliser
  --webp WEBP           Conversion en webp avec une certaine qualité (exemple
                        : --webp 75)
  --tree                Pour créer l'arborescence dans le répertoire de
                        téléchargement
  --force-title FORCE_TITLE
                        Le titre à utiliser dans les noms de fichier, à la
                        place de celui trouvé sur la page
  --encoding ENCODING   L'encoding du fichier d'entrée de liste d'URLs (ex : "utf-8")

SESSION_ID est la valeur de "c03aab1711dbd2a02ea11200dde3e3d1" dans le cookie.
Ces valeurs peuvent être stockées dans le fichier de configuration "izneo_get.cfg".
"""
import importlib
import re
import os
import sys
import shutil
from typing import List, Optional, Tuple
from .config_from_args import get_args
from .tools import check_version, create_cbz
from .plugins.site_processor import SiteProcessor
from .config import Config, OutputFormat
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
    # Vérification que c'est la dernière version.
    check_version(__version__)

    args_config, url, config_file = get_args()
    config = get_config(args_config, config_file)
    if not url:
        config_query = ConfigQuery(config, CONFIG_FILE)
        config = config_query.update_config_by_command()

    while not url:
        url = input("URL: ")

    # Liste des URLs à récupérer.
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
        print("OK")

        # Si besoin, on crée une archive.
        if config.output_format in [OutputFormat.CBZ, OutputFormat.BOTH]:
            expected_cbz_name = save_path.strip(".cbz") + ".cbz"
            if config.continue_from_existing and os.path.exists(expected_cbz_name):
                print(f'File "{expected_cbz_name}" already exists.')
            else:
                create_cbz(save_path)

        # Si besoin, on supprime le répertoire des images.
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
