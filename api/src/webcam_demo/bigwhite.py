"""Data source for Big White webcam data"""

from __future__ import annotations

import re
from io import BytesIO
from typing import Optional
from urllib.parse import urlparse

import requests
from PIL.Image import Image, open as open_image
from sqlmodel import Field, Session, select, SQLModel

from webcam_demo.db import engine, insert


_digits = re.compile("[0-9]+")
_DEFAULT_TIMEOUT_SECS = 5.0
_BIG_WHITE_WEBCAM_INDEX_URL: str = (
    "https://www.bigwhite.com/mountain-conditions/webcams"
)


class BigWhiteScrapingError(Exception):
    """an error occurred while scraping Big White's website"""


class BigWhiteWebcam(SQLModel, table=True):
    """A data source for webcam imagery from Big White."""

    __tablename__ = "bigwhite"

    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(unique=True, index=True)
    url_format: str
    last_index: int = Field(default=0)

    def format_url(self, index: int) -> str:
        """The image URL for the chosen webcam's current image index."""
        return self.url_format.format(index)

    def read(self, index, timeout: float = _DEFAULT_TIMEOUT_SECS) -> Image:
        """fetches the raw image data for this webcam"""
        response = requests.get(self.format_url(index), timeout=timeout)
        response.raise_for_status()
        self.last_index = max(index, self.last_index)
        return open_image(BytesIO(response.content))


_webcam_urls: dict[str, str] = {
    "Village Centre": "http://www.bigwhite.com/sites/default/files/village_{}.jpg",
    "Pow Cam": "http://www.bigwhite.com/sites/default/files/powpow_{}.jpg",
    "The Cliff": "http://www.bigwhite.com/sites/default/files/cliff_{}.jpg",
    "Easy Street": "http://www.bigwhite.com/sites/default/files/hwy33_{}.jpg",
    "Happy Valley": "http://www.bigwhite.com/sites/default/files/happyvalley_{}.jpg",
    "Bullet": "http://www.bigwhite.com/sites/default/files/bullet_{}.jpg",
    "Tube Park": "http://www.bigwhite.com/sites/default/files/tubepark_{}.jpg",
    "TELUS Park": "http://www.bigwhite.com/sites/default/files/teluspark_{}.jpg",
    "Snow Ghost": "http://www.bigwhite.com/sites/default/files/snowghost_{}.jpg",
    "Black Forest": "http://www.bigwhite.com/sites/default/files/blackforest_{}.jpg",
    "Gem Lake Top": "http://www.bigwhite.com/sites/default/files/gemlake_{}.jpg",
    "Gem Lake Bottom": "http://www.bigwhite.com/sites/default/files/westridge_{}.jpg",
}


def create_webcams() -> None:
    """Create or update the webcams in the database."""
    webcams = [
        {"name": name, "url_format": url_format}
        for name, url_format in _webcam_urls.items()
    ]
    with Session(engine) as session:
        statement = insert(BigWhiteWebcam).values(webcams)
        upsert = statement.on_conflict_do_update(
            index_elements=[BigWhiteWebcam.name],
            set_=dict(url_format=statement.excluded.url_format),
        )
        session.exec(upsert)
        session.commit()


def update_indices(timeout: float | None = None) -> None:
    """Scrape the latest webcam image indices and update the database."""
    if timeout is None:
        timeout = _DEFAULT_TIMEOUT_SECS
    response = requests.get(_BIG_WHITE_WEBCAM_INDEX_URL, timeout=timeout)
    response.raise_for_status()
    with Session(engine) as session:
        for webcam in session.exec(select(BigWhiteWebcam)):
            url_format = webcam.url_format
            url_prefix = url_format[: url_format.index("{}")]
            # URLs on the index page are in site-relative form
            url_prefix = urlparse(url_prefix).path
            try:
                image_index_position = response.text.index(url_prefix) + len(url_prefix)
            except ValueError as e:
                raise BigWhiteScrapingError(
                    f"error scraping image index for webcam: {webcam.name}"
                ) from e
            image_index = _digits.match(response.text, image_index_position)
            if image_index is None:
                raise BigWhiteScrapingError(
                    f"error scraping image index for webcam: {webcam.name}"
                )
            webcam.last_index = int(image_index.group(0))
            session.add(webcam)
        session.commit()
