"""Data source for Big White webcam data"""

import re
from enum import auto, Enum
from io import BytesIO
from urllib.parse import urlparse

import requests
from PIL.Image import Image, open as open_image


_digits = re.compile("[0-9]+")
_DEFAULT_TIMEOUT_SECS = 5.0


class BigWhite:
    """A data source for webcam imagery from Big White."""

    class Webcam(Enum):
        """identifier for a specific webcam at Big White"""

        VILLAGE_CENTRE = auto()
        POW_CAM = auto()
        THE_CLIFF = auto()
        EASY_STREET = auto()
        HAPPY_VALLEY = auto()
        BULLET = auto()
        TUBE_PARK = auto()
        TELUS_PARK = auto()
        SNOW_GHOST = auto()
        BLACK_FOREST = auto()
        GEM_LAKE_TOP = auto()
        GEM_LAKE_BOTTOM = auto()

    class BigWhiteScrapingError(Exception):
        """an error occurred while scraping Big White's website"""

    _INDEX_URL: str = "https://www.bigwhite.com/mountain-conditions/webcams"
    _URL_FORMATS: dict[Webcam, str] = {
        Webcam.VILLAGE_CENTRE: "https://www.bigwhite.com/sites/default/files/village_{}.jpg",
        Webcam.POW_CAM: "http://www.bigwhite.com/sites/default/files/powpow_{}.jpg",
        Webcam.THE_CLIFF: "http://www.bigwhite.com/sites/default/files/cliff_{}.jpg",
        Webcam.EASY_STREET: "http://www.bigwhite.com/sites/default/files/hwy33_{}.jpg",
        Webcam.HAPPY_VALLEY: "http://www.bigwhite.com/sites/default/files/happyvalley_{}.jpg",
        Webcam.BULLET: "http://www.bigwhite.com/sites/default/files/bullet_{}.jpg",
        Webcam.TUBE_PARK: "http://www.bigwhite.com/sites/default/files/tubepark_{}.jpg",
        Webcam.TELUS_PARK: "http://www.bigwhite.com/sites/default/files/teluspark_{}.jpg",
        Webcam.SNOW_GHOST: "http://www.bigwhite.com/sites/default/files/snowghost_{}.jpg",
        Webcam.BLACK_FOREST: "http://www.bigwhite.com/sites/default/files/blackforest_{}.jpg",
        Webcam.GEM_LAKE_TOP: "http://www.bigwhite.com/sites/default/files/gemlake_{}.jpg",
        Webcam.GEM_LAKE_BOTTOM: "http://www.bigwhite.com/sites/default/files/westridge_{}.jpg",
    }
    _webcam_indices: dict[Webcam, int] = {w: 0 for w in Webcam}

    def __init__(
        self, webcam: Webcam, index: int | None = None, timeout: float | None = None
    ):
        self._webcam = webcam
        self._timeout = timeout
        if timeout is None:
            self._timeout = _DEFAULT_TIMEOUT_SECS
        if index is None:
            BigWhite._scrape_indices(self._timeout)
            self.index = BigWhite._webcam_indices[self._webcam]
        else:
            self.index = index

    @staticmethod
    def _scrape_indices(timeout=None):
        if timeout is None:
            timeout = _DEFAULT_TIMEOUT_SECS
        response = requests.get(BigWhite._INDEX_URL, timeout=timeout)
        response.raise_for_status()
        for webcam in BigWhite.Webcam:
            url_format = BigWhite._URL_FORMATS[webcam]
            url_prefix = url_format[: url_format.index("{}")]
            # URLs on the index page are in site-relative form
            url_prefix = urlparse(url_prefix).path
            try:
                image_index_position = response.text.index(url_prefix) + len(url_prefix)
            except ValueError as e:
                raise BigWhite.BigWhiteScrapingError(
                    f"error scraping image index for webcam: {webcam.name}"
                ) from e
            image_index = _digits.match(response.text, image_index_position)
            if image_index is None:
                raise BigWhite.BigWhiteScrapingError(
                    f"error scraping image index for webcam: {webcam.name}"
                )
            BigWhite._webcam_indices[webcam] = int(image_index.group(0))

    @property
    def formatted_url(self) -> str:
        """The image URL for the chosen webcam's current image index."""
        return self._url_format.format(self.index)

    @property
    def _url_format(self):
        return BigWhite._URL_FORMATS[self._webcam]

    def read(self) -> Image:
        """fetches the raw image data for this webcam"""
        response = requests.get(self.formatted_url, timeout=self._timeout)
        response.raise_for_status()
        return open_image(BytesIO(response.content))
