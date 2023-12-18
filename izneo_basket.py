# -*- coding: utf-8 -*-
__version__ = "0.08.0"
"""
Source : https://github.com/izneo-get/izneo-get

Ce script permet de récupérer une liste d'URLS sur https://www.izneo.com/fr/ en
fonction d'une page de panier fini.

usage: izneo_basket.py [-h] [--session-id SESSION_ID] [--config CONFIG] url

Script pour obtenir une liste de BDs Izneo.

positional arguments:
  url                La page de panier fini qui contient une liste de BDs

options:
  -h, --help            show this help message and exit
  --session-id SESSION_ID, -s SESSION_ID
                        L'identifiant de session
  --config CONFIG       Fichier de configuration
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import re
import os
import sys
import argparse
import configparser
from bs4 import BeautifulSoup
import json


def requests_retry_session(
    retries=3,
    backoff_factor=1,
    status_forcelist=(500, 502, 504),
    session=None,
):
    """Permet de gérer les cas simples de problèmes de connexions."""
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def parse_from_id(session, id):
    url = f"https://www.izneo.com/fr/api/web/purchase-complete-details/{id}"
    r = requests_retry_session(session=session).get(url, allow_redirects=True)
    content = json.loads(r.text)
    new_results = 0

    if 'error' in content:
        print(f'Error: {content["error"]}')
        return 0

    for vol in content["albums"]:
        link = root_path + vol["url"]
        title = vol["title"]
        if title and link:
            print(link)
            new_results += 1
    return new_results


if __name__ == "__main__":
    session_id = ""
    root_path = "https://www.izneo.com"

    # Parse des arguments passés en ligne de commande.
    parser = argparse.ArgumentParser(description="""Script pour obtenir une liste de BDs Izneo.""")
    parser.add_argument("url", type=str, default=None, help="La page de panier qui contient une liste de BDs")
    parser.add_argument("--session-id", "-s", type=str, default=None, help="L'identifiant de session")
    parser.add_argument("--config", type=str, default=None, help="Fichier de configuration")
    args = parser.parse_args()

    # Lecture de la config.
    config = configparser.RawConfigParser()
    if args.config:
        config_name = args.config
    else:
        # config_name = re.sub(r"\.py$", ".cfg", os.path.basename(sys.argv[0]).replace("izneo_list", "izneo_get"))
        config_name = re.sub(r"\.py$", ".cfg", os.path.abspath(sys.argv[0]).replace("izneo_list", "izneo_get"))
        # config_name = re.sub(r"\.py$", ".cfg", os.path.abspath(sys.argv[0]))
    config.read(config_name)

    def get_param_or_default(config, param_name, default_value, cli_value=None):
        if cli_value is None:
            return config.get("DEFAULT", param_name) if config.has_option("DEFAULT", param_name) else default_value
        else:
            return cli_value

    session_id = get_param_or_default(config, "session_id", "", args.session_id)
    url = args.url

# Création d'une session et création du cookie.
    s = requests.Session()
    cookie_obj = requests.cookies.create_cookie(domain=".izneo.com", name="lang", value="fr")
    s.cookies.set_cookie(cookie_obj)
    cookie_obj = requests.cookies.create_cookie(
        domain=".izneo.com", name="c03aab1711dbd2a02ea11200dde3e3d1", value=session_id
    )
    s.cookies.set_cookie(cookie_obj)

    if re.match(r"^http[s]://www.izneo.com/fr/panier-fin/(\d+)", url):
        new_results = 0
        # On est dans un cas où on a une URL de série.
        id = re.findall("(\d+)/", url)
        if not id:
            id = re.findall("(\d+)", url)
        id = id[0]
        new_results += parse_from_id(s, id)
