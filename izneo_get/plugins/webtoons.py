# -*- coding: utf-8 -*-
import os
import re
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from PIL import Image

from ..book_infos import BookInfos
from ..config import Config
from .site_processor import SiteProcessor


class Webtoons(SiteProcessor):
    URL_PATTERNS = ["https://www.webtoons.com/*"]
    url: str
    config: Config
    cache_file: str
    headers: Dict[str, str] = {}
    _book_infos: Optional[BookInfos] = None

    def __init__(self, url: str = "", config: Optional[Config] = None):
        super().__init__(url, config)
        self.headers = {
            "Referer": "https://www.webtoons.com/",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "image",
        }

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return any(re.match(pattern, url) is not None for pattern in Webtoons.URL_PATTERNS)

    def authenticate(self) -> None: ...

    def before_download(self) -> None: ...

    def after_download(self, files_downloaded: List[str]) -> None:
        if not files_downloaded:
            return

        # Sort files alphabetically
        sorted_files = sorted(files_downloaded)

        # Open all images and get dimensions
        images = []
        max_width = 0
        total_height = 0

        for file_path in sorted_files:
            try:
                img = Image.open(file_path)
                images.append(img)
                width, height = img.size
                max_width = max(max_width, width)
                total_height += height
            except Exception as e:
                print(f"Error opening image {file_path}: {e}")
                continue

        if not images:
            return

        # Create composite image
        composite = Image.new("RGB", (max_width, total_height))
        y_offset = 0

        for img in images:
            # Center image if it's narrower than max_width
            x_offset = (max_width - img.size[0]) // 2
            composite.paste(img, (x_offset, y_offset))
            y_offset += img.size[1]
            img.close()  # Close image to free memory

        # Save composite image
        output_path = sorted_files[0].rsplit(".", 1)[0] + "_composite.jpg"
        composite.save(output_path, "JPEG", quality=100)
        composite.close()

        # Delete original files
        for file_path in sorted_files:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

        definitive_output_path = sorted_files[0].rsplit(".", 1)[0] + ".jpg"
        if os.path.exists(definitive_output_path):
            os.remove(definitive_output_path)
        os.rename(output_path, definitive_output_path)

    def download(self, forced_title: Optional[str] = None) -> str:
        return super().download(forced_title)

    def get_book_infos(self) -> BookInfos:
        if self._book_infos:
            return self._book_infos

        # Fetch page content
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract data from JavaScript object
        title = ""
        subtitle = ""
        language = ""
        description = ""
        chapter = ""

        # Find the script tag containing the JavaScript object
        script_tags = soup.find_all("script", type="text/javascript")
        for script in script_tags:
            if script.string and "window.__challengeViewerState__" in script.string:
                script_content = script.string
                if title_match := re.search(r"title\s*:\s*['\"]([^'\"]+)['\"]", script_content):
                    title = title_match[1]
                if subtitle_match := re.search(r"episodeTitle\s*:\s*['\"]([^'\"]+)['\"]", script_content):
                    subtitle = subtitle_match[1]
                if subtitle_match:
                    subtitle = subtitle_match[1]
                if language_match := re.search(r"languageCode\s*:\s*['\"]([^'\"]+)['\"]", script_content):
                    language = language_match[1]
                if desc_match := re.search(r"titleSynopsis\s*:\s*['\"]([^'\"]+)['\"]", script_content):
                    description = desc_match[1].replace("\\n", "\n").replace('\\"', '"')
                if chapter_match := re.search(r"episodeNo\s*:\s*(\d+)", script_content):
                    chapter = chapter_match[1]
                break

        # Find all img tags within div#_imageList and extract data-url attributes
        page_urls = []
        image_list_div = soup.find("div", id="_imageList")
        if image_list_div:
            img_tags = image_list_div.find_all("img")
            for img in img_tags:
                if data_url := img.get("data-url"):
                    page_urls.append(data_url)

        # If no images found, fallback to the original URL
        if not page_urls:
            page_urls = [self.url]

        self._book_infos = BookInfos(
            title=title,
            subtitle=subtitle,
            pages=len(page_urls),
            volume=chapter,
            chapter=chapter,
            language=language,
            read_direction=None,
            description=description,
            page_urls=page_urls,
            custom_fields={"metadata": {}, "book_id": None},
        )
        return self._book_infos


def init(url: str = "", config: Optional[Config] = None) -> Webtoons:
    return Webtoons(url, config)
