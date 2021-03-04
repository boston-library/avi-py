import os
import tempfile
import .constants as avi_const
import logging
import json

from pathlib import Path
from image_processing.exceptions import KakaduError
from image_processing import conversion, validation
from image_processing.kakadu import Kakadu
from PIL import Image


class AviJp2Image:
    def __init__(self, input_file_path: str, ) -> None:
        self.input_file_path = input_file_path
        self.kakadu = Kakadu(kakadu_base_path=kakadu_base_path)
        self.logger = logging.getLogger(__name__)

    def convert_to_jp2(self):
        pass

    def preprocess(self, img: Image):
        pass

    def _src_quality(self, img: Image) -> str:
        if img.mode == "RGBA":
            return "color"
        elif img.mode == "L":
            return "gray"
        else:
            raise IOError("Unknown Image mode {0}".format(img.mode))

    def __layer_rates(self, layer_count: int, compression_numerator: int) -> str:
        rates = []
        cmp = 24.0 / float(compression_numerator)
        for _ in range(layer_count):
            rates.append(cmp)
            cmp = round((cmp / 1.618), 8)
        string_cmps = [str(cmp) for cmp in rates]
        return ",".join(string_cmps)

    def __level_count_for_size(self, long_dim: int) -> int:
        levels = 0
        level_size = long_dim
        while (level_size >= 96):
            level_size = level_size / 2
            levels = levels + 1
        return levels - 1

    def __long_dim(self, img: Image) -> int:
        return max(img.width, img.height)
