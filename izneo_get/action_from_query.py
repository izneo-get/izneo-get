from enum import Enum
import inquirer
from typing import Optional

try:
    from action import Action
except ImportError:
    from .action import Action


class ActionQuery:
    @staticmethod
    def get_action() -> Optional[Action]:
        questions = [
            inquirer.List(
                "action",
                message="What do you want to do?",
                choices=[
                    ("Download + Convert + Pack", Action.PROCESS),
                    ("Get book infos only", Action.INFOS),
                    ("Download book only", Action.DOWNLOAD),
                    ("Convert book only", Action.CONVERT),
                    ("Pack book only", Action.PACK),
                    ("EXIT", None),
                ],
                carousel=True,
                default=Action.PROCESS,
            )
        ]
        anwser = inquirer.prompt(questions)
        return anwser["action"]


if __name__ == "__main__":
    print(ActionQuery.get_action())
