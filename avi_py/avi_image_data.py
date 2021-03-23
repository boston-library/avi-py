import os
import errno
from pathlib import Path
from typing import Union
from PIL import Image
from image_processing import validation

from avi_py import constants as avi_const

class AviImageData:
    """
    Class for storing all low level image data for functions that are used to populate
    Additional Kakau options
    """
    def __init__(self, image_src_path: Union[str, Path],
                tile_size: int=avi_const.KDU_DEFAULT_TILE_SIZE,
                layer_count: int=avi_const.KDU_DEFAULT_LAYER_COUNT,
                compression_numerator: int=avi_const.IMAGE_DEFAULT_COMPRESSION) -> None:
        self.image_src_path = image_src_path
        self.tile_size = tile_size
        self.layer_count = layer_count
        self.compression_numerator = compression_numerator
        with Image.open(self.image_src_path) as image_src:
            self.src_quality = image_src
            self.long_dim = image_src
            self.icc_profile = image_src

    @property
    def image_src_path(self) -> Path:
        return self._image_src_path

    @image_src_path.setter
    def image_src_path(self, image_src_path: Union[str, Path]) -> None:
        if not isinstance(image_src_path, Path):
            image_src_path = Path(image_src_path)
        if not image_src_path.is_file():
            raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), str(image_src_path))
        self._image_src_path = image_src_path

    @property
    def tile_size(self) -> str:
        return f'{self._tile_size},{self._tile_size}'

    @tile_size.setter
    def tile_size(self, tile_size: int) -> None:
        self._tile_size = tile_size

    @property
    def icc_profile(self) -> Union[None, bytes]:
        return self._icc_profile

    @icc_profile.setter
    def icc_profile(self, img: Image) -> None:
        self._icc_profile = img.info.get('icc_profile')

    @property
    def src_quality(self) -> str:
        return self._src_quality

    @src_quality.setter
    def src_quality(self, img: Image) -> None:
        if img.mode in avi_const.COLOR_MODES:
            self._src_quality = 'color'
        elif img.mode == validation.GREYSCALE:
            self._src_quality = 'gray'
        else:
            raise IOError(f'Unknown Image mode {img.mode}')

    @property
    def long_dim(self) -> int:
        return self._long_dim

    @long_dim.setter
    def long_dim(self, img: Image) -> None:
        self._long_dim = max(img.width, img.height)

    @property
    def layer_count(self) -> int:
        return self._layer_count

    @layer_count.setter
    def layer_count(self, layer_count: int) -> None:
        self._layer_count = layer_count

    @property
    def compression_numerator(self) -> int:
        return self._compression_numerator

    @compression_numerator.setter
    def compression_numerator(self, compression_numerator: int) -> None:
        self._compression_numerator = compression_numerator

    def image_ext(self) -> str:
        return self.image_src_path.suffix

    def valid_image_ext(self) -> bool:
        return self.image_ext() in avi_const.VALID_IMAGE_EXTENSIONS

    def jp2_space(self) -> str:
        return 'sRGB' if self.src_quality == 'color' else 'sLUM'

    def needs_icc_profile(self) -> bool:
        return self.src_quality == 'color' and self.icc_profile is None

    def level_count_for_size(self) -> int:
        levels = 0
        level_size = self.long_dim
        while level_size >= avi_const.IMAGE_MAX_LEVEL_SIZE:
            level_size = level_size / 2
            levels = levels + 1
        return levels - 1

    def layer_rates(self) -> str:
        rates = []
        cmp = 24.0 / float(self.compression_numerator)
        for _ in range(self.layer_count):
            rates.append(cmp)
            cmp = round((cmp / 1.618), 8)
        return ",".join([str(cmp) for cmp in rates])
