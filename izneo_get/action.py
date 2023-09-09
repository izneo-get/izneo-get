from enum import Enum
from typing import Optional, Type


class Action(Enum):
    INFOS = "INFOS"
    DOWNLOAD = "DOWNLOAD"
    CONVERT = "CONVERT"
    PACK = "PACK"
    PROCESS = "PROCESS"

    @staticmethod
    def from_str(value: str) -> "Action":
        default_action = Action.PROCESS
        if not value:
            return default_action
        value = value.upper()
        if value == "INFOS":
            return Action.INFOS
        elif value == "DOWNLOAD":
            return Action.DOWNLOAD
        elif value == "CONVERT":
            return Action.CONVERT
        elif value == "PACK":
            return Action.PACK
        elif value == "PROCESS":
            return Action.PROCESS
        else:
            return default_action
