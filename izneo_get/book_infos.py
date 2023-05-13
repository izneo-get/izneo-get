from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class ReadDirection(Enum):
    LTOR = 1
    RTOL = 2


@dataclass
class BookInfos:
    title: str
    pages: int
    serie: str = ""
    volume: str = ""
    chapter: str = ""
    genre: str = ""
    release_date: str = ""
    subtitle: str = ""
    authors: str = ""
    isbn: str = ""
    language: str = ""
    description: str = ""
    publisher: str = ""
    read_direction: ReadDirection = ReadDirection.LTOR
    custom_fields: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        ignore_attrs = {"custom_fields", "description", "read_direction"}
        infos = "\n".join(
            f"{{{attr}}}: {str(self.__dict__[attr])}"
            for attr in self.__dict__
            if self.__dict__[attr] and attr not in ignore_attrs
        )
        infos += f"\n{{read_direction}}: " + str(self.read_direction).split(".")[-1]
        return infos
