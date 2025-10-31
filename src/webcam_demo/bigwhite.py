"""Data source for Big White webcam data"""

import re
from enum import auto, Enum
from io import BytesIO
from urllib.parse import urlparse

import requests
from PIL.Image import Image, open as open_image


_digits = re.compile("[0-9]+")


class BigWhite:
    class Webcam(Enum):
        """identifier for a specific webcam at Big White"""
        VillageCentre = auto()
        PowCam = auto()
        TheCliff = auto()
        EasyStreet = auto()
        HappyValley = auto()
        Bullet = auto()
        TubePark = auto()
        TelusPark = auto()
        SnowGhost = auto()
        BlackForest = auto()
        GemLakeTop = auto()
        GemLakeBottom = auto()

    class BigWhiteScrapingError(Exception):
        """an error occurred while scraping Big White's website"""

    _INDEX_URL: str = "https://www.bigwhite.com/mountain-conditions/webcams"
    _URL_FORMATS: dict[Webcam, str] = {
        Webcam.VillageCentre: "https://www.bigwhite.com/sites/default/files/village_{}.jpg",
        Webcam.PowCam: "http://www.bigwhite.com/sites/default/files/powpow_{}.jpg",
        Webcam.TheCliff: "http://www.bigwhite.com/sites/default/files/cliff_{}.jpg",
        Webcam.EasyStreet: "http://www.bigwhite.com/sites/default/files/hwy33_{}.jpg",
        Webcam.HappyValley: "http://www.bigwhite.com/sites/default/files/happyvalley_{}.jpg",
        Webcam.Bullet: "http://www.bigwhite.com/sites/default/files/bullet_{}.jpg",
        Webcam.TubePark: "http://www.bigwhite.com/sites/default/files/tubepark_{}.jpg",
        Webcam.TelusPark: "http://www.bigwhite.com/sites/default/files/teluspark_{}.jpg",
        Webcam.SnowGhost: "http://www.bigwhite.com/sites/default/files/snowghost_{}.jpg",
        Webcam.BlackForest: "http://www.bigwhite.com/sites/default/files/blackforest_{}.jpg",
        Webcam.GemLakeTop: "http://www.bigwhite.com/sites/default/files/gemlake_{}.jpg",
        Webcam.GemLakeBottom: "http://www.bigwhite.com/sites/default/files/westridge_{}.jpg",
    }
    _webcam_indices: dict[Webcam, int] = {w: 0 for w in Webcam}

    def __init__(self, webcam: Webcam, index: int | None = None):
        self._webcam = webcam
        if index is None:
            BigWhite._scrape_indices()
            self.index = BigWhite._webcam_indices[self._webcam]
        else:
            self.index = index

    @staticmethod
    def _scrape_indices():
        response = requests.get(BigWhite._INDEX_URL)
        response.raise_for_status()
        for webcam in BigWhite.Webcam:
            url_format = BigWhite._URL_FORMATS[webcam]
            url_prefix = url_format[:url_format.index("{}")]
            # URLs on the index page are in site-relative form
            url_prefix = urlparse(url_prefix).path
            try:
                image_index_position = response.text.index(url_prefix) + len(url_prefix)
            except ValueError as e:
                raise BigWhite.BigWhiteScrapingError(f"error scraping image index for webcam: {webcam.name}") from e
            image_index = _digits.match(response.text, image_index_position)
            if image_index is None:
                raise BigWhite.BigWhiteScrapingError(f"error scraping image index for webcam: {webcam.name}")
            else:
                BigWhite._webcam_indices[webcam] = int(image_index.group(0))

    @property
    def formatted_url(self) -> str:
        return self._url_format.format(self.index)

    @property
    def _url_format(self):
        return BigWhite._URL_FORMATS[self._webcam]

    def read(self) -> Image:
        """fetches the raw image data for this webcam"""
        response = requests.get(self.formatted_url)
        response.raise_for_status()
        return open_image(BytesIO(response.content))