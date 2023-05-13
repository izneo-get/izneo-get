import argparse

from izneo_get.config import Config, ImageFormat, OutputFormat


def get_args() -> tuple[Config, str, str]:
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
    parser.add_argument(
        "--ignore-cache",
        action="store_true",
        dest="ignore_cache",
        default=None,
        help="Pour ne pas utiliser le cache de session",
    )
    parsed = parser.parse_args()
    config = Config(
        output_folder=parsed.output_folder,
        output_filename=parsed.output_filename,
        image_format=ImageFormat.from_str(parsed.image_format),
        image_quality=parsed.image_quality,
        output_format=OutputFormat.from_str(parsed.output_format),
        pause_sec=parsed.pause,
        user_agent=parsed.user_agent,
        continue_from_existing=parsed.continue_from_existing,
        authentication_from_cache=False if parsed.ignore_cache == True else None,
    )
    return config, parsed.url, parsed.config
