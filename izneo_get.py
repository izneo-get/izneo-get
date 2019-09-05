# -*- coding: utf-8 -*-
__version__ = "0.01"
"""
Ce script permet de récupérer une BD présente sur https://www.izneo.com/fr/ dans la limite des capacités de notre compte existant.

usage: python izneo_get.py [-h] 
                [--cfduid CFDUID]
                [--session-id SESSION_ID] 
                [--output-folder OUTPUT_FOLDER]
                [--output-format {cbz,both,jpg}] [--config CONFIG]
                url

CFDUID est la valeur de "cfduid" dans le cookie.
SESSION_ID est la valeur de "c03aab1711dbd2a02ea11200dde3e3d1" dans le cookie.
Ces valeurs peuvent être stockées dans le fichier de configuration "izneo_get.cfg".
"""
import requests
import re
import os
import sys 
import html
import argparse
import configparser
import shutil


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
    return name


if __name__ == "__main__":
    cfduid = ""
    session_id = ""
    page_sup_to_grab = 20
    root_path = "https://www.izneo.com/fr/"

    # Parse des arguments passés en ligne de commande.
    parser = argparse.ArgumentParser(
    description="""Script pour sauvegarder une BD Izneo."""
    )
    parser.add_argument(
        "url", type=str, default=None, help="L'URL de la BD à récupérer"
    )
    parser.add_argument(
        "--session-id", "-s", type=str, default=None, help="L'identifiant de session"
    )
    parser.add_argument(
        "--cfduid", "-c", type=str, default=None, help="L'identifiant cfduid"
    )
    parser.add_argument(
        "--output-folder", "-o", type=str, default=None, help="Répertoire racine de téléchargement"
    )
    parser.add_argument(
        "--output-format", "-f", choices={"cbz", "jpg", "both"}, type=str, default="jpg", help="Répertoire racine de téléchargement"
    )
    parser.add_argument(
        "--config", type=str, default=None, help="Fichier de configuration"
    )
    args = parser.parse_args()

 
    # Lecture de la config.
    config = configparser.RawConfigParser()
    if args.config:
        config_name = args.config
    else:
        config_name = re.sub("\.py$", ".cfg", os.path.basename(sys.argv[0]))
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
    output_folder = get_param_or_default(config, "output_folder", os.path.dirname(os.path.abspath(sys.argv[0])), args.output_folder)
    url = args.url
    output_format = args.output_format

    # Création d'une session et création du cookie.
    s = requests.Session()
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='__cfduid', value=cfduid)
    s.cookies.set_cookie(cookie_obj)
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='lang', value='fr')
    s.cookies.set_cookie(cookie_obj)
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='c03aab1711dbd2a02ea11200dde3e3d1', value=session_id)
    s.cookies.set_cookie(cookie_obj)

    

    # On récupère les informations de la BD à récupérer.
    r = s.get(url, cookies=s.cookies, allow_redirects=True)
    html_one_line = r.text.replace("\n", "").replace("\r", "")
    
    # Le titre.
    title = re.findall("<meta property=\"og:title\" content=\"(.+?)\" />", html_one_line)
    if len(title) > 0:
        title = strip_tags(title[0]).strip()
    else:
        title = re.findall("<h1 class=\"product-title\" itemprop=\"name\">(.+?)</h1>", html_one_line)
        if len(title) > 0:
            title = strip_tags(title[0]).strip()
    title = html.unescape(title)
    title = clean_name(title)

    # L'ISBN, qui servira d'identifiant de la BD.
    isbn = re.findall("href=\"//reader.izneo.com/read/(.+?)\?exiturl", html_one_line)
    if len(isbn) > 0:
        isbn = strip_tags(isbn[0]).strip()

    # La série (si elle est spécifiée).
    serie = re.findall("<h2 class=\"product-serie\" itemprop=\"isPartOf\">(.+?)</div>", html_one_line)
    if len(serie) > 0:
        serie = strip_tags(serie[0]).strip()
        serie = " (" + re.sub("\s+", " ", serie) + ")"
    else:
        serie = ""
    serie = html.unescape(serie)

    # L'auteur (s'il est spécifié).
    author = re.findall("<div class=\"author\" itemprop=\"author\">(.+?)</div>", html_one_line)
    if len(author) > 0:
        author = strip_tags(author[0]).strip()
        author = " (" + re.sub("\s+", " ", author) + ")"
    else:
        author = ""
    author = html.unescape(author)

    # Le nombre de pages annoncé.
    nb_pages = re.findall("Nb de pages</h1>(.+?)</div>", html_one_line)
    if len(nb_pages) > 0:
        nb_pages = int(strip_tags(nb_pages[0]).strip())
    else:
        nb_pages = 999
    nb_digits = len(str(nb_pages + page_sup_to_grab))

    # Si on n'a pas les informations de base, on arrête tout de suite.
    if not title or not isbn: 
        print("ERROR Impossible de trouver le livre")
        exit()

    # Création du répertoire de destination.
    categories = url.replace(root_path, "").split("/")
    mid_path = ""
    for elem in categories[:-1]:
        res = re.findall("(.+)-\d+", elem)
        if len(res) > 0:
            elem = res[0]
        mid_path += elem
        if not os.path.exists(output_folder + "/" + mid_path): os.mkdir(output_folder + "/" + mid_path)
        mid_path += "/"

    save_path = output_folder + "/" + mid_path + clean_name(title + serie + author)
    if not os.path.exists(save_path): os.mkdir(save_path)

    # On boucle sur toutes les pages de la BD.
    for page in range(nb_pages + page_sup_to_grab):
    #for page in range(2):
        url = "https://reader.izneo.com/read/" + str(isbn) +  "/" + str(page) + "?quality=HD"
        r = s.get(url, cookies=s.cookies, allow_redirects=True)
        if r.status_code == 404:
            if page < nb_pages:
                print("[WARNING] On a récupéré " + str(page + 1) + " pages (au moins " + str(nb_pages) + " attendues)")
            break
        if re.findall("<!DOCTYPE html>", r.text):
            print("[WARNING] Page " + str(page + 1) + " inaccessible")
            break

        page_txt = ("000000000" + str(page))[-nb_digits:]
        file = open(save_path + "/" + title + " - " + page_txt + ".jpg", "wb").write(r.content)

    # Si besoin, on crée une archive.
    if output_format == "cbz" or output_format == "both":
        shutil.make_archive(save_path, 'zip', save_path)
        os.rename(save_path + ".zip", save_path + ".cbz")

    # Si besoin, on supprime le répertoire des JPG.
    if output_format == "cbz":
        shutil.rmtree(save_path)





