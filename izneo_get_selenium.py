# -*- coding: utf-8 -*-
__version__ = "1.01.0"
"""
Source : https://github.com/izneo-get/izneo-get

Ce script permet de récupérer une BD présente sur https://www.izneo.com/fr/ dans la limite des capacités de notre compte existant.
Cette version utilise Selenium pour piloter un driver Chrome.

usage: izneo_get_selenium.py [-h] [--session-id SESSION_ID] [--cfduid CFDUID]
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
  --cfduid CFDUID, -c CFDUID
                        L'identifiant cfduid
  --output-folder OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        Répertoire racine de téléchargement
  --output-format {jpg,both,cbz}, -f {jpg,both,cbz}
                        Répertoire racine de téléchargement
  --config CONFIG       Fichier de configuration
  --from-page FROM_PAGE
                        Première page à récupérer (défaut : 1)
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

CFDUID est la valeur de "cfduid" dans le cookie.
SESSION_ID est la valeur de "c03aab1711dbd2a02ea11200dde3e3d1" dans le cookie.
Ces valeurs peuvent être stockées dans le fichier de configuration "izneo_get.cfg".
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
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageChops
import glob
from io import BytesIO
import base64


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
    return re.sub("<[^<]+?>", "", html)


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
    chars = '\\/:*<>?"|'
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


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


if __name__ == "__main__":
    cfduid = ""
    session_id = ""
    root_path = "https://www.izneo.com/"

    # Parse des arguments passés en ligne de commande.
    parser = argparse.ArgumentParser(
        description="""Script pour sauvegarder une BD Izneo."""
    )
    parser.add_argument(
        "url",
        type=str,
        default=None,
        help="L'URL de la BD à récupérer ou le chemin vers un fichier local contenant une liste d'URLs",
    )
    parser.add_argument(
        "--session-id", "-s", type=str, default=None, help="L'identifiant de session"
    )
    parser.add_argument(
        "--cfduid", "-c", type=str, default=None, help="L'identifiant cfduid"
    )
    parser.add_argument(
        "--output-folder",
        "-o",
        type=str,
        default=None,
        help="Répertoire racine de téléchargement",
    )
    parser.add_argument(
        "--output-format",
        "-f",
        choices={"cbz", "jpg", "both"},
        type=str,
        default="jpg",
        help="Répertoire racine de téléchargement",
    )
    parser.add_argument(
        "--config", type=str, default=None, help="Fichier de configuration"
    )
    parser.add_argument(
        "--from-page",
        type=int,
        default=1,
        help="Première page à récupérer (défaut : 1)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Nombre de pages à récupérer au maximum (défaut : 1000)",
    )
    parser.add_argument(
        "--pause",
        type=int,
        default=0,
        help="Pause (en secondes) à respecter après chaque téléchargement d'image",
    )
    parser.add_argument(
        "--full-only",
        action="store_true",
        default=False,
        help="Ne prend que les liens de BD disponible dans l'abonnement",
    )
    parser.add_argument(
        "--continue",
        action="store_true",
        dest="continue_from_existing",
        default=False,
        help="Pour reprendre là où on en était",
    )
    parser.add_argument(
        "--user-agent", type=str, default=None, help="User agent à utiliser"
    )
    parser.add_argument(
        "--webp",
        type=int,
        default=None,
        help="Conversion en webp avec une certaine qualité (exemple : --webp 75)",
    )
    parser.add_argument(
        "--tree",
        action="store_true",
        default=False,
        help="Pour créer l'arborescence dans le répertoire de téléchargement",
    )
    parser.add_argument(
        "--force-title",
        type=str,
        default=None,
        help="Le titre à utiliser dans les noms de fichier, à la place de celui trouvé sur la page",
    )
    parser.add_argument(
        "--encoding",
        type=str,
        default=None,
        help="L'encoding du fichier d'entrée de liste d'URLs (ex : \"utf-8\")",
    )
    parser.add_argument(
        "--dimension",
        type=int,
        default=4320,
        help="La taille de l'image attendue (défaut : 2160)",
    )
    args = parser.parse_args()

    # Lecture de la config.
    config = configparser.RawConfigParser()
    if args.config:
        config_name = args.config
    else:
        # config_name = re.sub(r"\.py$", ".cfg", os.path.basename(sys.argv[0]))
        config_name = re.sub(r"\.py$", ".cfg", os.path.abspath(sys.argv[0]))
        config_name = re.sub(r"\.exe$", ".cfg", config_name)
    config.read(config_name)

    def get_param_or_default(config, param_name, default_value, cli_value=None):
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
    pause_sec = get_param_or_default(config, "pause", "", args.pause)
    dimension = get_param_or_default(config, "pause", "", args.dimension)
    output_folder = get_param_or_default(
        config,
        "output_folder",
        os.path.dirname(os.path.abspath(sys.argv[0])) + "/DOWNLOADS",
        args.output_folder,
    )
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    url = args.url
    output_format = args.output_format
    nb_page_limit = args.limit
    from_page = args.from_page
    full_only = args.full_only
    continue_from_existing = args.continue_from_existing
    webp = args.webp
    tree = args.tree
    force_title = args.force_title
    encoding = args.encoding

    prefered_driver = "./bin/chromedriver.exe"
    prefered_driver = config.get("DEFAULT", "prefered_driver", fallback=prefered_driver)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3") # Seulement les erreurs fatales.
    chrome_driver = prefered_driver
    try:
        driver = webdriver.Chrome(chrome_driver, options=chrome_options)
    except:
        # Ce driver n'est pas compatible.
        print(f'Impossible de se connecter avec le driver "{chrome_driver}"')
        for filename in glob.iglob("./**/chromedriver*.exe", recursive=True):
            chrome_driver = filename
            try:
                driver = webdriver.Chrome(chrome_driver, options=chrome_options)
            except:
                print(f'Impossible de se connecter avec le driver "{chrome_driver}"')
                continue
            if filename != prefered_driver:
                prefered_driver = filename
                print(f"Vous pouvez ajouter / modifier la ligne suivante à votre fichier de configuration :")
                print(f"prefered_driver = {prefered_driver}")
            break

    driver.set_window_size(dimension, dimension)
    driver.get(url)
    driver.add_cookie({"name": "__cfduid", "value": cfduid, "domain": "izneo.com"})
    driver.add_cookie({"name": "lang", "value": "fr", "domain": "izneo.com"})
    driver.add_cookie(
        {
            "name": "c03aab1711dbd2a02ea11200dde3e3d1",
            "value": session_id,
            "domain": "izneo.com",
        }
    )

    config["DEFAULT"]["prefered_driver"] = prefered_driver
    # with open(config_name, "w") as configfile:
    #     config.write(configfile)

    # Création d'une session et création du cookie.
    s = requests.Session()
    cookie_obj = requests.cookies.create_cookie(
        domain=".izneo.com", name="__cfduid", value=cfduid
    )
    s.cookies.set_cookie(cookie_obj)
    cookie_obj = requests.cookies.create_cookie(
        domain=".izneo.com", name="lang", value="fr"
    )
    s.cookies.set_cookie(cookie_obj)
    cookie_obj = requests.cookies.create_cookie(
        domain=".izneo.com", name="c03aab1711dbd2a02ea11200dde3e3d1", value=session_id
    )
    s.cookies.set_cookie(cookie_obj)

    # Liste des URLs à récupérer.
    url_list = []
    if os.path.exists(url):
        if encoding:
            with open(url, "r", encoding=encoding) as f:
                lines = f.readlines()
        else:
            with open(url, "r") as f:
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
                url_list.append([line, next_forced_title])
                next_forced_title = ""
    else:
        url_list.append([url, force_title])

    for url in url_list:
        force_title = url[1]
        url = url[0]
        print("URL: " + url)
        page_sup_to_grab = 20
        # On récupère les informations de la BD à récupérer.
        # r = s.get(url, cookies=s.cookies, allow_redirects=True)
        r = requests_retry_session(session=s).get(
            url, cookies=s.cookies, allow_redirects=True
        )
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
        title = re.findall("<title>(.+?)- (.*) à lire en ligne</title>", html_one_line)
        if title:
            title = strip_tags(title[0][0]).strip()
        else:
            title = re.findall(
                '<h1 class="product-title" itemprop="name">(.+?)</h1>', html_one_line
            )
            if title:
                title = strip_tags(title[0]).strip()
            else:
                title = re.findall(
                    '<meta property="og:title" content="(.+?)" />', html_one_line
                )
                if len(title) > 0:
                    title = strip_tags(title[0]).strip()
                else:
                    title = ""
        title = html.unescape(title)
        title = clean_name(title)

        # Le tome.
        tome = re.findall('<div class="widget"(.+?)</div>', html_one_line)
        if tome:
            tome = re.findall(
                '<section class="widget__section">(.+?)</section>', tome[0]
            )
            if tome:
                tome = strip_tags(tome[0]).strip() + ""
                tome = tome.replace(":", " ").replace("/", "-")
                tome = html.unescape(tome)
                tome = clean_name(tome)
                tome = (" - " + tome) if tome != title else ""
            else:
                tome = ""
        else:
            tome = ""

        # C'est toujours l'auteur qui se trouve dans le champ "série".
        # La série (si elle est spécifiée).
        author = re.findall(
            '<h2 class="product-serie" itemprop="isPartOf">(.+?)</div>', html_one_line
        )
        if author:
            author = strip_tags(author[0]).strip()
            author = " (" + re.sub(r"\s+", " ", author) + ")"
        else:
            author = ""
        author = html.unescape(author)
        author = clean_name(author)

        serie = ""

        # # L'auteur (s'il est spécifié).
        # author = re.findall("<div class=\"author\" itemprop=\"author\">(.+?)</div>", html_one_line)
        # if author:
        #     author = strip_tags(author[0]).strip()
        #     author = " (" + re.sub(r"\s+", " ", author) + ")"
        # else:
        #     author = ""
        # author = html.unescape(author)
        # author = clean_name(author)

        # Le nombre de pages annoncé.
        nb_pages = re.findall("Nb de pages</dt>(.+?)</dd>", html_one_line)
        if len(nb_pages) > 0:
            nb_pages = int(strip_tags(nb_pages[0]).strip())
        else:
            nb_pages = 999
        nb_digits = max(3, len(str(nb_pages + page_sup_to_grab)))
        page_sup_to_grab = 999

        # Si on n'a pas les informations de base, on arrête tout de suite.
        if not title:
            print("ERROR Impossible de trouver le livre")
            break

        # Création du répertoire de destination.
        categories = url.replace(root_path, "").split("/")
        mid_path = ""
        if tree:
            for elem in categories[:-1]:
                res = re.findall(r"(.+)-\d+", elem)
                if len(res) > 0:
                    elem = res[0]
                mid_path += elem
                if not os.path.exists(output_folder + "/" + mid_path):
                    os.mkdir(output_folder + "/" + mid_path)
                mid_path += "/"

        if force_title:
            print(
                'Téléchargement de "'
                + clean_name(title + serie + author)
                + '" en tant que "'
                + clean_name(force_title)
                + '"'
            )
            title = clean_name(force_title)
            save_path = output_folder + "/" + mid_path + title
        else:
            print(
                'Téléchargement de "' + clean_name(title + serie + tome + author) + '"'
            )
            save_path = (
                output_folder
                + "/"
                + mid_path
                + clean_name(title + serie + tome + author)
            )

        print("{nb_pages} pages attendues".format(nb_pages=nb_pages))

        # Si l'archive existe déjà, on ne télécharge pas cette BD.
        if continue_from_existing and os.path.exists(save_path + ".cbz"):
            print(save_path + ".cbz existe déjà, on passe")
            continue
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        print("Destination : " + save_path)

        # Les changements sont essentiellement à partir d'ici.

        # Reset du bookmark
        url_id = re.search(".+-(.+)", url)[1]
        data = {"book": url_id, "page": 0}
        r = requests_retry_session(session=s).post(
            "https://www.izneo.com/book/updatebookmark",
            cookies=s.cookies,
            allow_redirects=True,
            json=data,
        )

        progress_bar = ""
        # On boucle sur toutes les pages de la BD.
        for page in range(min(nb_pages + page_sup_to_grab, nb_page_limit)):
            page_num = page + from_page

            page_txt = ("000000000" + str(page_num))[-nb_digits:]
            store_path = save_path + "/" + title + " " + page_txt + ".jpg"
            store_path_webp = save_path + "/" + title + " " + page_txt + ".webp"

            page_url = url + "/read/" + str(page_num) + "?exiturl=" + url
            # Si la page existe déjà sur le disque, on passe.
            if continue_from_existing and (
                (
                    not webp
                    and os.path.exists(store_path)
                    and os.path.getsize(store_path)
                )
                or (
                    webp
                    and os.path.exists(store_path_webp)
                    and os.path.getsize(store_path_webp)
                )
            ):
                progress_bar += "x"
                progress_message = (
                    "\r"
                    + "[page "
                    + str(page_num)
                    + " / ~"
                    + str(nb_pages)
                    + "] "
                    + progress_bar
                    + " "
                )
                # print("x", end="")
                print(progress_message, end="")
                sys.stdout.flush()
                continue

            driver.get(page_url)
            time.sleep(0.5)
            loaded = False
            attempts = 20
            while not loaded and attempts > 0:
                try:
                    canvas = driver.find_element_by_id("iz_canv")
                    if len(canvas.screenshot_as_base64) > 10000:
                        loaded = True
                except:
                    print("Waiting...")
                    time.sleep(0.5)

            if loaded == False or page_url != driver.current_url:
                print()
                if page_url != driver.current_url:
                    print(f"[ERROR] Impossible de récupérer la page {page}")
                if page < nb_pages:
                    print(
                        "[WARNING] On a récupéré "
                        + str(page)
                        + " pages ("
                        + str(nb_pages)
                        + " annoncées par l'éditeur)"
                    )
                break


            canvas_base64 = driver.execute_script(
                "return arguments[0].toDataURL('image/png').substring(21);", canvas
            )
            # On enlève les 21 premiers caractères qui sont "data:image/png;base64".

            canvas_png = base64.b64decode(canvas_base64)
            im = Image.open(BytesIO(canvas_png))
            im = trim(im)
            # im.save("screenshot.png", optimize=True)

            # Si demandé, on converti en webp.
            if webp:
                im.save(store_path_webp, "webp", quality=webp)
            else:
                rgb_im = im.convert("RGB")
                rgb_im.save(store_path, quality=100, optimize=True, progressive=True)

            progress_bar += "."
            progress_message = (
                "\r"
                + "[page "
                + str(page_num)
                + " / ~"
                + str(nb_pages)
                + "] "
                + progress_bar
                + " "
            )
            # print(".", end="")
            print(progress_message, end="")
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
                while (
                    os.path.exists(save_path + filler_txt + ".zip") and max_attempts > 0
                ):
                    filler_txt += "_"
                    max_attempts -= 1
            shutil.make_archive(save_path + filler_txt, "zip", save_path)

            filler_txt2 = ""
            if os.path.exists(save_path + ".cbz"):
                filler_txt2 += "_"
                max_attempts = 20
                while (
                    os.path.exists(save_path + filler_txt2 + ".cbz")
                    and max_attempts > 0
                ):
                    filler_txt2 += "_"
                    max_attempts -= 1
            os.rename(save_path + filler_txt + ".zip", save_path + filler_txt2 + ".cbz")

        # Si besoin, on supprime le répertoire des JPG.
        if output_format == "cbz":
            shutil.rmtree(save_path)
    driver.quit()
    print("Terminé !")
