"""Data source for Big White webcam data"""

from enum import auto, Enum

import requests


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

    def __init__(self, webcam: Webcam, index: int = 0):
        self._webcam = webcam
        self.index = index

    def _format_url(self) -> str:
        return BigWhite._URL_FORMATS[self._webcam].format(self.index)

    def read(self) -> bytes:
        """fetches the raw image data for this webcam"""
        response = requests.get(self._format_url())
        response.raise_for_status()
        return response.content