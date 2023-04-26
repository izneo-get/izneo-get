from dataclasses import dataclass
from enum import Enum


class ImageFormat(Enum):
    ORIGIN = 1
    JPEG = 2
    WEBP = 3


class OutputFormat(Enum):
    IMAGES = 1
    CBZ = 2
    BOTH = 3


@dataclass
class Config:
    output_folder: str = "DOWNLOADS"
    output_filename: str = "{title} - {volume}. {subtitle}"
    image_format: ImageFormat = ImageFormat.ORIGIN
    image_quality: int = 100
    output_format: OutputFormat = OutputFormat.BOTH
    pause_sec: int = 1
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    )
    continue_from_existing: bool = False
    authentication_from_cache: bool = True
    cache_folder: str = ".cache"
