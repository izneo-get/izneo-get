import configparser
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class ImageFormat(Enum):
    ORIGIN = "ORIGIN"
    JPEG = "JPEG"
    WEBP = "WEBP"

    @staticmethod
    def from_str(value: str) -> Optional["ImageFormat"]:
        if not value:
            return None
        value = value.upper()
        if value == "ORIGIN":
            return ImageFormat.ORIGIN
        elif value in {"JPEG", "JPG"}:
            return ImageFormat.JPEG
        elif value == "WEBP":
            return ImageFormat.WEBP
        else:
            return None


class OutputFormat(Enum):
    IMAGES = "IMAGES"
    CBZ = "CBZ"
    BOTH = "BOTH"

    @staticmethod
    def from_str(value: str) -> Optional["OutputFormat"]:
        if not value:
            return None
        value = value.upper()
        if value == "IMAGES":
            return OutputFormat.IMAGES
        elif value == "CBZ":
            return OutputFormat.CBZ
        elif value == "BOTH":
            return OutputFormat.BOTH
        else:
            return None


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

    def to_dict(self):
        value: Dict[str, Any] = {key: str(val) for key, val in self.__dict__.items() if val is not None}
        return value

    def save_config(self, path: str) -> None:
        config = configparser.RawConfigParser()
        config_as_dict = self.to_dict()
        del config_as_dict["cache_folder"]
        config["DEFAULT"] = config_as_dict
        with open(path, "w") as f:
            config.write(f)
