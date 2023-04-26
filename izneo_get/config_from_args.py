import argparse
from argparse import Namespace


def get_args() -> Namespace:
    # Parse des arguments passés en ligne de commande.
    parser = argparse.ArgumentParser(description="""Script pour sauvegarder une BD Izneo.""")
    parser.add_argument(
        "url",
        type=str,
        default=None,
        nargs="?",
        help="L'URL de la BD à récupérer ou le chemin vers un fichier local contenant une liste d'URLs",
    )
    parser.add_argument("--config", type=str, default=None, help="Fichier de configuration")
    # parser.add_argument("--session-id", "-s", type=str, default=None, help="L'identifiant de session")
    parser.add_argument(
        "--output-folder",
        "-o",
        type=str,
        default=None,
        help="Répertoire racine de téléchargement",
    )
    parser.add_argument(
        "--output-filename",
        type=str,
        default=None,
        help="Nom du fichier ou répertoire de sortie",
    )
    parser.add_argument(
        "--image-format",
        choices={"origin", "jpeg", "webp"},
        type=str,
        default=None,
        help="Conversion des images au format JPEG ou WEBP",
    )
    parser.add_argument(
        "--image-quality",
        type=int,
        default=None,
        help="Qualité de conversion des images (100 = maximum)",
    )
    parser.add_argument(
        "--output-format",
        "-f",
        choices={"cbz", "images", "both"},
        type=str,
        default=None,
        help="Format de sortie",
    )
    parser.add_argument(
        "--pause",
        type=int,
        default=None,
        help="Pause (en secondes) à respecter après chaque téléchargement d'image",
    )
    parser.add_argument("--user-agent", type=str, default=None, help="User agent à utiliser")
    parser.add_argument(
        "--continue",
        action="store_true",
        dest="continue_from_existing",
        default=None,
        help="Pour éviter de télécharger un fichier déjà existant",
    )
    # parser.add_argument(
    #     "--from-page",
    #     type=int,
    #     default=0,
    #     help="Première page à récupérer (défaut : 0)",
    # )
    # parser.add_argument(
    #     "--limit",
    #     type=int,
    #     default=1000,
    #     help="Nombre de pages à récupérer au maximum (défaut : 1000)",
    # )
    # parser.add_argument(
    #     "--full-only",
    #     action="store_true",
    #     default=False,
    #     help="Ne prend que les liens de BD disponible dans l'abonnement",
    # )
    # parser.add_argument(
    #     "--webp",
    #     type=int,
    #     default=None,
    #     help="Conversion en webp avec une certaine qualité (exemple : --webp 75)",
    # )
    # parser.add_argument(
    #     "--tree",
    #     action="store_true",
    #     default=False,
    #     help="Pour créer l'arborescence dans le répertoire de téléchargement",
    # )
    # parser.add_argument(
    #     "--force-title",
    #     type=str,
    #     default=None,
    #     help="Le titre à utiliser dans les noms de fichier, à la place de celui trouvé sur la page",
    # )
    # parser.add_argument(
    #     "--encoding",
    #     type=str,
    #     default=None,
    #     help="L'encoding du fichier d'entrée de liste d'URLs (ex : \"utf-8\")",
    # )
    return parser.parse_args()
