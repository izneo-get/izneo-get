# -*- coding: utf-8 -*-
__version__ = "0.04"
"""
Source : https://github.com/izneo-get/izneo-get

Ce script permet de récupérer une liste d'URLS sur https://www.izneo.com/fr/ en fonction d'une recherche ou d'une page de série.

usage: izneo_list.py [-h] [--session-id SESSION_ID] [--cfduid CFDUID]
                     [--config CONFIG] [--pause PAUSE] [--full-only]
                     [--series] [--force-title]
                     search

Script pour obtenir une liste de BDs Izneo.

positional arguments:
  search                La page de série qui contient une liste de BDs

optional arguments:
  -h, --help            show this help message and exit
  --session-id SESSION_ID, -s SESSION_ID
                        L'identifiant de session
  --cfduid CFDUID, -c CFDUID
                        L'identifiant cfduid
  --config CONFIG       Fichier de configuration
  --pause PAUSE         Pause (en secondes) à respecter après chaque appel de
                        page
  --full-only           Ne prend que les liens de BD disponible dans
                        l'abonnement
  --series              La recherche ne se fait que sur les séries
  --force-title         Ajoute l'élément "--force-tilte" dans la sortie
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import re
import os
import sys 
import html
import argparse
import configparser
import shutil
import time
from bs4 import BeautifulSoup
import json

def strip_tags(html):
    """Permet de supprimer tous les tags HTML d'une chaine de caractère.

    Parameters
    ----------
    html : str
        La chaine de caractère d'entrée.

    Returns
    -------
    str
        La chaine purgée des tous les tags HTML.
    """
    return re.sub('<[^<]+?>', '', html)

def clean_name(name):
    """Permet de supprimer les caractères interdits dans les chemins.

    Parameters
    ----------
    name : str
        La chaine de caractère d'entrée.

    Returns
    -------
    str
        La chaine purgée des tous les caractères non désirés.
    """
    chars = "\\/:*<>?\"|"
    for c in chars:
        name = name.replace(c, "_")
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\.+$", "", name)
    return name

def requests_retry_session(
    retries=3,
    backoff_factor=1,
    status_forcelist=(500, 502, 504),
    session=None,
):
    """Permet de gérer les cas simples de problèmes de connexions.
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def parse_html(html, force_title=False):
    new_results = 0
    soup = BeautifulSoup(html, features="html.parser")
    for div in soup.find_all("div", class_="product-list-albums"):
        is_abo = div.find_all("div", class_="corner abo")
        is_abo = True if is_abo else False
        link = div.find_all("a")
        link = root_path + link[0].get("href") if link else ""
        title = div.find_all("h4", class_="product_title")
        title = title[0].text if title else ""
        title = strip_tags(title)
        if not is_abo:
            title += " (*)"
        if title and force_title:
            title += " --force-title " + title
        title = re.sub(r"\s+", " ", title).strip()
        if title and link and ((not full_only) or (full_only and is_abo)):
            print("# " + title)
            print(link)
        if title and link:
            new_results += 1
    return new_results


def parse_html_json(html, force_title=False):
    content = json.loads(html)
    new_results = 0
    for current_type in ['volume', 'outside']:
        for vol in content['albums'][current_type]:
            is_abo = vol['inSubscription']
            link = root_path + vol['url']
            title = vol['serie_name'] + ' - '
            title = title  + ('[' + str(vol['volume']) + '] ' if 'volume' and vol['volume'] in vol else '')
            title = title + vol['title']
            if not is_abo:
                title += " (*)"
            if title and force_title:
                title += " --force-title " + title
            title = re.sub(r"\s+", " ", title).strip()
            if title and link and ((not full_only) or (full_only and is_abo)):
                print("# " + title)
                print(link)
            if title and link:
                new_results += 1
    return new_results


if __name__ == "__main__":
    cfduid = ""
    session_id = ""
    page_sup_to_grab = 20
    root_path = "https://www.izneo.com"

    # Parse des arguments passés en ligne de commande.
    parser = argparse.ArgumentParser(
    description="""Script pour obtenir une liste de BDs Izneo."""
    )
    parser.add_argument(
        "search", type=str, default=None, help="La page de série qui contient une liste de BDs"
    )
    parser.add_argument(
        "--session-id", "-s", type=str, default=None, help="L'identifiant de session"
    )
    parser.add_argument(
        "--cfduid", "-c", type=str, default=None, help="L'identifiant cfduid"
    )
    parser.add_argument(
        "--config", type=str, default=None, help="Fichier de configuration"
    )
    parser.add_argument(
        "--pause", type=int, default=0, help="Pause (en secondes) à respecter après chaque appel de page"
    )
    parser.add_argument(
        "--full-only", action="store_true", default=False, help="Ne prend que les liens de BD disponible dans l'abonnement"
    )
    parser.add_argument(
        "--series", action="store_true", default=False, help="La recherche ne se fait que sur les séries"
    )
    parser.add_argument(
        "--force-title", action="store_true", default=False, help="Ajoute l'élément \"--force-tilte\" dans la sortie"
    )
    args = parser.parse_args()

 
    # Lecture de la config.
    config = configparser.RawConfigParser()
    if args.config:
        config_name = args.config
    else:
        config_name = re.sub(r"\.py$", ".cfg", os.path.basename(sys.argv[0]).replace("izneo_list", "izneo_get"))
    config.read(config_name)

    def get_param_or_default(
        config, param_name, default_value, cli_value=None
    ):
        if cli_value is None:
            return (
                config.get("DEFAULT", param_name)
                if config.has_option("DEFAULT", param_name)
                else default_value
            )
        else:
            return cli_value

    cfduid = get_param_or_default(config, "cfduid", "", args.cfduid)
    session_id = get_param_or_default(config, "session_id", "", args.session_id)
    search = args.search
    pause_sec = args.pause
    full_only = args.full_only
    series = args.series
    force_title = args.force_title

    # Création d'une session et création du cookie.
    s = requests.Session()
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='__cfduid', value=cfduid)
    s.cookies.set_cookie(cookie_obj)
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='lang', value='fr')
    s.cookies.set_cookie(cookie_obj)
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='c03aab1711dbd2a02ea11200dde3e3d1', value=session_id)
    s.cookies.set_cookie(cookie_obj)

    if re.match("^http[s]*://.*", search):
        new_results = 0
        # On est dans un cas où on a une URL de série.
        id = re.findall(".+-(\d+)/", search)
        if not id:
            id = re.findall(".+-(\d+)", search)
        id = id[0]
        url = "https://www.izneo.com/fr/api/serie/album/" + str(id) + "?order=2&abo=1" # + ("&abo=1" if full_only else "")
        r = requests_retry_session(session=s).post(url, allow_redirects=True)
        new_results += parse_html_json(r.text, force_title=force_title)
    else:
        url = "https://www.izneo.com/fr/search-album-list"
        if series:
            url = "https://www.izneo.com/fr/search-series-list"
        step = 0
        new_results = 0
        while step == 0 or new_results > 0:
            new_results = 0
            data = {
                'limit_start':step * 25,
                'limit_end':'25',
                'text':search,
            }
            # r = s.post(url, allow_redirects=True, data=data)
            r = requests_retry_session(session=s).post(url, allow_redirects=True, data=data)

            html_one_line = r.text.replace("\n", "").replace("\r", "")
            new_results += parse_html(html_one_line, force_title=force_title)
            time.sleep(pause_sec)
            step += 1