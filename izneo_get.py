# -*- coding: utf-8 -*-
__version__ = "0.04"
"""
Ce script permet de récupérer une BD présente sur https://www.izneo.com/fr/ dans la limite des capacités de notre compte existant.

Utilisation : python izneo_get.py [-h] 
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
    root_path = "https://www.izneo.com/"

    # Parse des arguments passés en ligne de commande.
    parser = argparse.ArgumentParser(
    description="""Script pour sauvegarder une BD Izneo."""
    )
    parser.add_argument(
        "url", type=str, default=None, help="L'URL de la BD à récupérer ou le chemin vers un fichier local contenant une liste d'URLs"
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
    parser.add_argument(
        "--from-page", type=int, default=0, help="Première page à récupérer (défaut : 0)"
    )
    parser.add_argument(
        "--limit", type=int, default=1000, help="Nombre de pages à récupérer au maximum (défaut : 1000)"
    )
    parser.add_argument(
        "--pause", type=int, default=0, help="Pause (en secondes) à respecter après chaque téléchargement d'image"
    )
    parser.add_argument(
        "--full-only", action="store_true", default=False, help="Ne prend que les liens de BD disponible dans l'abonnement"
    )
    parser.add_argument(
        "--continue", action="store_true", dest="continue_from_existing", default=False, help="Pour reprendre là où on en était"
    )
    parser.add_argument(
        "--user-agent", type=str, default=None, help="User agent à utiliser"
    )
    args = parser.parse_args()

 
    # Lecture de la config.
    config = configparser.RawConfigParser()
    if args.config:
        config_name = args.config
    else:
        config_name = re.sub(r"\.py$", ".cfg", os.path.basename(sys.argv[0]))
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
    user_agent = get_param_or_default(config, "user_agent", "", args.user_agent)
    output_folder = get_param_or_default(config, "output_folder", os.path.dirname(os.path.abspath(sys.argv[0])) + "/DOWNLOADS", args.output_folder)
    if not os.path.exists(output_folder): os.mkdir(output_folder)
    url = args.url
    output_format = args.output_format
    nb_page_limit = args.limit
    from_page = args.from_page
    pause_sec = args.pause
    full_only = args.full_only
    continue_from_existing = args.continue_from_existing

    # Création d'une session et création du cookie.
    s = requests.Session()
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='__cfduid', value=cfduid)
    s.cookies.set_cookie(cookie_obj)
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='lang', value='fr')
    s.cookies.set_cookie(cookie_obj)
    cookie_obj = requests.cookies.create_cookie(domain='.izneo.com', name='c03aab1711dbd2a02ea11200dde3e3d1', value=session_id)
    s.cookies.set_cookie(cookie_obj)

    # Liste des URLs à récupérer.
    url_list = []
    if os.path.exists(url):
        with open(url, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line and line[0] != '#':
                url_list.append(line)
    else:
        url_list.append(url)



    for url in url_list:
        print("URL: " + url)
        # On récupère les informations de la BD à récupérer.
        r = s.get(url, cookies=s.cookies, allow_redirects=True)
        html_one_line = r.text.replace("\n", "").replace("\r", "")
        
        soup = BeautifulSoup(html_one_line, features="html.parser")

        is_abo = False
        div = soup.find("div", id="product_cover")
        if div:
            is_abo = div.find_all("div", class_="corner abo")
            is_abo = True if is_abo else False
        
        if not is_abo:
            print("Cette BD n'est pas disponible dans l'abonnement")
        if full_only and not is_abo:
            continue

        # Le titre.
        title = re.findall("<h1 class=\"product-title\" itemprop=\"name\">(.+?)</h1>", html_one_line)
        if title:
            title = strip_tags(title[0]).strip()
        else:
            title = re.findall("<meta property=\"og:title\" content=\"(.+?)\" />", html_one_line)
            if len(title) > 0:
                title = strip_tags(title[0]).strip()
            else:
                title = ""
        title = html.unescape(title)
        title = clean_name(title)

        # L'ISBN, qui servira d'identifiant de la BD.
        isbn = re.findall("href=\"//reader.izneo.com/read/(.+?)\\?exiturl", html_one_line)
        isbn = strip_tags(isbn[0]).strip() if isbn else ""

        # La série (si elle est spécifiée).
        serie = re.findall("<h2 class=\"product-serie\" itemprop=\"isPartOf\">(.+?)</div>", html_one_line)
        if serie:
            serie = strip_tags(serie[0]).strip()
            serie = " (" + re.sub(r"\s+", " ", serie) + ")"
        else:
            serie = ""
        serie = html.unescape(serie)

        # L'auteur (s'il est spécifié).
        author = re.findall("<div class=\"author\" itemprop=\"author\">(.+?)</div>", html_one_line)
        if author:
            author = strip_tags(author[0]).strip()
            author = " (" + re.sub(r"\s+", " ", author) + ")"
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
            break

        # Création du répertoire de destination.
        categories = url.replace(root_path, "").split("/")
        mid_path = ""
        for elem in categories[:-1]:
            res = re.findall(r"(.+)-\d+", elem)
            if len(res) > 0:
                elem = res[0]
            mid_path += elem
            if not os.path.exists(output_folder + "/" + mid_path): os.mkdir(output_folder + "/" + mid_path)
            mid_path += "/"

        print("Téléchargement de \"" + clean_name(title + serie + author) + "\"")
        # print(str(nb_pages) + " pages attendues")
        print("{nb_pages} pages attendues".format(nb_pages=nb_pages))
        save_path = output_folder + "/" + mid_path + clean_name(title + serie + author)
        if not os.path.exists(save_path): os.mkdir(save_path)
        print("Destination : " + save_path)


        headers = {
            # 'Accept': 'image/webp,*/*',
            'Connection': 'keep-alive',
            'Referer': 'https://reader.izneo.com/read/' + isbn + '?exiturl=' + url,
        }
        if user_agent:
            headers['User-Agent'] = user_agent

        params = (
            ('quality', 'HD'),
        )
        # On boucle sur toutes les pages de la BD.
        for page in range(min(nb_pages + page_sup_to_grab, nb_page_limit)):
            page_num = page + from_page

            page_txt = ("000000000" + str(page_num))[-nb_digits:]
            store_path = save_path + "/" + title + " - " + page_txt + ".jpg"

            url = "https://reader.izneo.com/read/" + str(isbn) +  "/" + str(page_num) + "?quality=HD"
            # Si la page existe déjà sur le disque, on passe.
            if continue_from_existing and os.path.exists(store_path):
                print("x", end="")
                sys.stdout.flush()
                continue

            r = s.get(url, cookies=s.cookies, allow_redirects=True, params=params, headers=headers)
            if r.status_code == 404:
                if page < nb_pages:
                    print("[WARNING] On a récupéré " + str(page + 1) + " pages (" + str(nb_pages) + " annoncées par l'éditeur)")
                break
            # if re.findall("<!DOCTYPE html>", r.text):
            # if "<!DOCTYPE html>" in r.text:
            if r.encoding:
                print("[WARNING] Page " + str(page_num) + " inaccessible")
                break
            file = open(store_path, "wb").write(r.content)
            print(".", end="")
            sys.stdout.flush()
            time.sleep(pause_sec)
        print("OK")

        # Si besoin, on crée une archive.
        if output_format == "cbz" or output_format == "both":
            print("Création du CBZ")
            # Dans le cas où un fichier du même nom existe déjà, on change de nom.
            filler_txt = ""
            if os.path.exists(save_path + ".zip"):
                filler_txt += "_"
                max_attempts = 20
                while os.path.exists(save_path + filler_txt + ".zip") and max_attempts > 0:
                    filler_txt += "_"
                    max_attempts -= 1
            shutil.make_archive(save_path + filler_txt, 'zip', save_path)

            filler_txt2 = ""
            if os.path.exists(save_path + ".cbz"):
                filler_txt2 += "_"
                max_attempts = 20
                while os.path.exists(save_path + filler_txt2 + ".cbz") and max_attempts > 0:
                    filler_txt2 += "_"
                    max_attempts -= 1
            os.rename(save_path + filler_txt + ".zip", save_path + filler_txt2 + ".cbz")

        # Si besoin, on supprime le répertoire des JPG.
        if output_format == "cbz":
            shutil.rmtree(save_path)

    print("Terminé !")

