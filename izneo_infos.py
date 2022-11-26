# -*- coding: utf-8 -*-
__version__ = "0.01"
"""
Source : https://github.com/izneo-get/izneo-get

usage: izneo_infos.py [-h] [--output OUTPUT_FILE] URL

Script pour obtenir les infos sur une BD Izneo.

positional arguments:
  URL                   L'URL d'une BD.

options:
  -h, --help            show this help message and exit
  --output OUTPUT_FILE, -o OUTPUT_FILE
                        Enregistrer le résultat dans un fichier.
"""
import requests
import re
import argparse
from bs4 import BeautifulSoup
import json


def parse_html(html):
    infos = {}
    soup = BeautifulSoup(html, features="html.parser")
    for div in soup.find_all("div", class_="details-row"):
        elem = div.find("p").text.strip()
        value = div.text.replace(elem, "").strip()
        value = " ".join(value.split())
        if value:
            infos[elem] = value

    return infos


def get_infos_from_id(book_id: int, sign: str = ""):
    r = requests.get(
        f"https://www.izneo.com/book/{book_id}" + (f"?{sign}" if sign else ""),
        allow_redirects=True,
    )
    book_infos = json.loads(r.text)["data"]
    items = ["title", "subtitle", "serie_name", "volume", "shelf_name", "gender_name", "readDirection", "synopsis"]
    filtered_infos = {i: book_infos[i].strip() for i in items if i in book_infos}
    return filtered_infos


def get_infos_from_url(url: str):
    book_infos = {}
    r = requests.get(url, allow_redirects=True)
    if r.status_code not in [200, 201]:
        print("Impossible de récupérer la page")
        return book_infos
    book_infos = parse_html(r.text)
    return book_infos


def main():
    # Parse des arguments passés en ligne de commande.
    parser = argparse.ArgumentParser(description="""Script pour obtenir les infos sur une BD Izneo.""")
    parser.add_argument("url", metavar="URL", type=str, default=None, help="L'URL d'une BD.")
    parser.add_argument(
        "--output", "-o", type=str, metavar="OUTPUT_FILE", default="", help="Enregistrer le résultat dans un fichier."
    )
    args = parser.parse_args()

    url = args.url
    output_file = args.output

    if not re.match("^http[s]*://.*", url):
        print("URL invalide")
        return
    id = re.findall(".+-(\d+)", url)
    if not id:
        print("Impossible de trouver l'identifiant du livre...")
        return
    id = id[0]
    sign = ""
    if re.match("(.+)login=cvs&sign=([^&]*)", url):
        sign = re.match("(.+)login=cvs&sign=([^&]*)", url)[2]
        sign = "login=cvs&sign=" + sign

    infos = get_infos_from_url(url)
    infos.update(get_infos_from_id(id, sign))
    for key, val in infos.items():
        print(f"{key:20} : {val}")
    if output_file:
        if not output_file.lower().endswith(".json"):
            output_file += ".json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(infos, f, indent=4, ensure_ascii=False)
        print()
        print(f'Les informations ont été enregistrées dans le fichier "{output_file}".')


if __name__ == "__main__":
    main()
