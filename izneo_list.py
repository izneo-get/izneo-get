# -*- coding: utf-8 -*-
__version__ = "0.01"
"""

"""
import requests
import re
import os
import sys 
import html
import argparse
import configparser
import shutil
import time
from bs4 import BeautifulSoup

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
    return name


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

    # Création d'une session et création du cookie.
    s = requests.Session()
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='__cfduid', value=cfduid)
    s.cookies.set_cookie(cookie_obj)
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='lang', value='fr')
    s.cookies.set_cookie(cookie_obj)
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='c03aab1711dbd2a02ea11200dde3e3d1', value=session_id)
    s.cookies.set_cookie(cookie_obj)

    if re.match("^http[s]*://.*", search):
        # On est dans un cas où on a une URL de série.
        url = search

        step = 0
        new_results = 0
        while step == 0 or new_results > 0:
            new_results = 0
            data = {
                'limit_album_start':step * 16,
            }
            r = s.post(url, allow_redirects=True, data=data)

            html_one_line = r.text.replace("\n", "").replace("\r", "")
            soup = BeautifulSoup(html_one_line, features="html.parser")
            for div in soup.find_all("div", class_="product-list-item"):
                is_abo = div.find_all("div", class_="corner abo")
                is_abo = True if is_abo else False
                link = div.find_all("a", class_="view-details")
                link = root_path + link[0].get("href") if link else ""
                title = div.find_all("div", class_="product-title")
                title = title[0].text if title else ""
                title = strip_tags(title)
                if not is_abo:
                    title += " (*)"
                title = re.sub(r"\s+", " ", title).strip()
                if title and link and ((not full_only) or (full_only and is_abo)):
                    print("# " + title)
                    print(link)
                if title and link:
                    new_results += 1
            step += 1

    else:
        url = "https://www.izneo.com/fr/search-album-list"
    
    # TODO
    url = search
    # url = "https://www.izneo.com/fr/search-album-list"
    # data = {
    #     'limit_start':'0',
    #     'limit_end':'20',
    #     'text':'largo'
    # }
    # r = s.post(url, allow_redirects=True, data=data)
    # html_one_line = r.text.replace("\n", "").replace("\r", "")
    
    # Le titre.
    # title = re.findall("<meta property=\"og:title\" content=\"(.+?)\" />", html_one_line)
    # if len(title) > 0:
    #     title = strip_tags(title[0]).strip()
    # else:
    #     title = re.findall("<h1 class=\"product-title\" itemprop=\"name\">(.+?)</h1>", html_one_line)
    #     if len(title) > 0:
    #         title = strip_tags(title[0]).strip()
    #     else:
    #         title = ""
    # title = html.unescape(title)
    # title = clean_name(title)
