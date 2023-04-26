from enum import Enum
import inquirer
import re
from typing import Callable

try:
    from config import Config, ImageFormat, OutputFormat
except ImportError:
    from .config import Config, ImageFormat, OutputFormat


class MenuItem(Enum):
    QUIT = 0
    OUTPUT_FOLDER = 1
    FILENAME_PATTERN = 2
    IMAGE_FORMAT = 3
    IMAGE_QUALITY = 4
    OUTPUT_FORMAT = 5
    PAUSE_SEC = 6
    USER_AGENT = 7
    CONTINUE_FROM_EXISTING = 8
    AUTHENTICATION_FROM_CACHE = 9


digit_validation = lambda _, x: re.match(r"^\d*$", x) is not None


class ConfigQuery:
    config: Config

    def __init__(self, config: Config):
        self.config = config

    def update_config_by_command(self) -> Config:
        choice: MenuItem = None
        while choice != MenuItem.QUIT:
            questions = [
                inquirer.List(
                    "action",
                    message="What parameter do you want to update",
                    choices=[
                        (f"Output folder: {self.config.output_folder}", MenuItem.OUTPUT_FOLDER),
                        (f"Filename pattern: {self.config.output_filename}", MenuItem.FILENAME_PATTERN),
                        (f"Image format: {str(self.config.image_format).split('.')[-1]}", MenuItem.IMAGE_FORMAT),
                        (f"Image quality: {self.config.image_quality}", MenuItem.IMAGE_QUALITY),
                        (f"Output format: {str(self.config.output_format).split('.')[-1]}", MenuItem.OUTPUT_FORMAT),
                        (f"Pause (sec): {self.config.pause_sec}", MenuItem.PAUSE_SEC),
                        (f"User agent: {self.config.user_agent}", MenuItem.USER_AGENT),
                        (
                            f"Continue from existing: {self.config.continue_from_existing}",
                            MenuItem.CONTINUE_FROM_EXISTING,
                        ),
                        (
                            f"Authentication from cache: {self.config.authentication_from_cache}",
                            MenuItem.AUTHENTICATION_FROM_CACHE,
                        ),
                        (">> DONE <<", MenuItem.QUIT),
                    ],
                    carousel=True,
                    default=choice or MenuItem.QUIT,
                )
            ]
            answer = inquirer.prompt(questions)
            if not answer:
                break
            choice = answer["action"]
            self.update_item(choice)
        return self.config

    def update_item(self, item: MenuItem):
        actions = {
            MenuItem.OUTPUT_FOLDER: self.update_item_output_folder,
            MenuItem.FILENAME_PATTERN: self.update_item_filename_pattern,
            MenuItem.IMAGE_FORMAT: self.update_item_image_format,
            MenuItem.IMAGE_QUALITY: self.update_item_image_quality,
            MenuItem.OUTPUT_FORMAT: self.update_item_output_format,
            MenuItem.PAUSE_SEC: self.update_item_pause_sec,
            MenuItem.USER_AGENT: self.update_item_user_agent,
            MenuItem.CONTINUE_FROM_EXISTING: self.update_item_continue_from_existing,
            MenuItem.AUTHENTICATION_FROM_CACHE: self.update_item_authentication_from_cache,
            MenuItem.QUIT: self.update_item_quit,
        }
        actions[item]()

    def update_item_output_folder(self):
        self.config.output_folder = prompt_text("Output folder", self.config.output_folder)

    def update_item_filename_pattern(self):
        self.config.output_filename = prompt_text("Filename pattern", self.config.output_filename)

    def update_item_image_format(self):
        questions = [
            inquirer.List(
                "image_format",
                message="Image format",
                choices=[
                    ("ORIGIN", ImageFormat.ORIGIN),
                    ("JPEG", ImageFormat.JPEG),
                    ("WEBP", ImageFormat.WEBP),
                ],
                default=self.config.image_format,
                carousel=True,
            )
        ]
        answer = inquirer.prompt(questions)
        self.config.image_format = answer["image_format"] or self.config.image_format

    def update_item_image_quality(self):
        self.config.image_quality = int(prompt_text("Image quality", self.config.image_quality, digit_validation))

    def update_item_output_format(self):
        questions = [
            inquirer.List(
                "output_format",
                message="Output format",
                choices=[
                    ("IMAGES", OutputFormat.IMAGES),
                    ("CBZ", OutputFormat.CBZ),
                    ("BOTH", OutputFormat.BOTH),
                ],
                default=self.config.output_format,
                carousel=True,
            )
        ]
        answer = inquirer.prompt(questions)
        self.config.output_format = answer["output_format"] or self.config.output_format

    def update_item_pause_sec(self):
        self.config.pause_sec = int(prompt_text("Pause (sec)", self.config.pause_sec, digit_validation))

    def update_item_user_agent(self):
        self.config.user_agent = prompt_text("User agent", self.config.user_agent)

    def update_item_continue_from_existing(self):
        questions = [
            inquirer.List(
                "continue_from_existing",
                message="Continue from existing",
                choices=[
                    ("True", True),
                    ("False", False),
                ],
                default=self.config.continue_from_existing,
                carousel=True,
            )
        ]
        answer = inquirer.prompt(questions)
        self.config.continue_from_existing = answer["continue_from_existing"]

    def update_item_authentication_from_cache(self):
        questions = [
            inquirer.List(
                "authentication_from_cache",
                message="Authentication from cache",
                choices=[
                    ("True", True),
                    ("False", False),
                ],
                default=self.config.authentication_from_cache,
                carousel=True,
            )
        ]
        answer = inquirer.prompt(questions)
        self.config.authentication_from_cache = answer["authentication_from_cache"]

    def update_item_quit(self):
        pass


def prompt_text(message: str, default: str = "", validate: Callable = lambda _, x: True) -> str:
    questions = [
        inquirer.Text(
            "value",
            message=message,
            validate=validate,
        )
    ]
    answers = inquirer.prompt(questions)
    return answers["value"] or default


if __name__ == "__main__":
    config = Config()
    query = ConfigQuery(config)
    query.update_config_by_command()
