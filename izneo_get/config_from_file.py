import configparser
import re
import os
import sys
from typing import Optional
from .config import Config, ImageFormat, OutputFormat
from argparse import Namespace


def get_config_from_file(config_file: str, args_config: Optional[Config] = None) -> Config:
    default_config = Config()
    # Lecture de la config.
    config = configparser.RawConfigParser()
    if config_file:
        config_name = config_file
    else:
        # config_name = re.sub(r"\.py$", ".cfg", os.path.basename(sys.argv[0]))
        config_name = re.sub(r"\.py$", ".cfg", os.path.abspath(sys.argv[0]))
        config_name = re.sub(r"\.exe$", ".cfg", config_name)
    config.read(config_name)

    def get_param_or_default(config, param_name, default_value, cli_value=None):
        if cli_value is None:
            return config.get("DEFAULT", param_name) if config.has_option("DEFAULT", param_name) else default_value
        else:
            return cli_value

    output_folder = get_param_or_default(
        config,
        "output_folder",
        default_config.output_folder,
        args_config.output_folder if args_config else None,
    )

    output_filename = get_param_or_default(
        config, "output_filename", default_config.output_filename, args_config.output_filename if args_config else None
    )
    image_format = get_param_or_default(
        config,
        "image_format",
        default_config.image_format.value,
        args_config.image_format.value if args_config and args_config.image_format else None,
    )
    image_format = ImageFormat.from_str(image_format) or default_config.image_format

    image_quality = int(
        get_param_or_default(
            config, "image_quality", default_config.image_quality, args_config.image_quality if args_config else None
        )
    )
    output_format = get_param_or_default(
        config,
        "output_format",
        default_config.output_format.value,
        args_config.output_format.value if args_config and args_config.output_format else None,
    )
    output_format = OutputFormat.from_str(output_format) or default_config.output_format
    pause_sec = int(
        get_param_or_default(
            config, "pause_sec", default_config.pause_sec, args_config.pause_sec if args_config else None
        )
    )
    user_agent = get_param_or_default(
        config, "user_agent", default_config.user_agent, args_config.user_agent if args_config else None
    )
    continue_from_existing = get_param_or_default(
        config,
        "continue_from_existing",
        default_config.continue_from_existing,
        args_config.continue_from_existing if args_config else None,
    )
    continue_from_existing = str(continue_from_existing).lower() in {
        "true",
        "1",
        "yes",
        "y",
    }
    authentication_from_cache = get_param_or_default(
        config,
        "authentication_from_cache",
        default_config.authentication_from_cache,
        args_config.authentication_from_cache if args_config else None,
    )
    authentication_from_cache = str(authentication_from_cache).lower() in {
        "true",
        "1",
        "yes",
        "y",
    }

    # session_id = get_param_or_default(config, "session_id", "", args_config.session_id)
    # nb_page_limit = args_config.limit
    # from_page = args_config.from_page
    # full_only = args_config.full_only

    # webp = args_config.webp
    # tree = args_config.tree
    # force_title = args_config.force_title
    # encoding = args_config.encoding

    return Config(
        output_folder=output_folder,
        output_filename=output_filename,
        image_format=image_format,
        image_quality=image_quality,
        output_format=output_format,
        pause_sec=pause_sec,
        user_agent=user_agent,
        continue_from_existing=continue_from_existing,
        authentication_from_cache=authentication_from_cache,
    )
