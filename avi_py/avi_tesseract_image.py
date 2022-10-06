import os
import errno
from tempfile import TemporaryDirectory, NamedTemporaryFile
from pathlib import Path
from typing import Union

from PIL import Image
import cv2
import numpy as np

class AviTesseractImage:
    """
    Class for pre processing and splitting up tiffs for tesseract OCR
    """
    def __init__(self, image_src_path: Union[str, Path]) -> None:
        self.image_src_path = image_src_path
        self._temp_directory = TemporaryDirectory(prefix='avi_tess_image', dir='/tmp')

    def __enter__(self):
        return self.preprocess_image()

    def __exit__(self, *args):
        self._temp_directory.cleanup()

    @property
    def image_src_path(self) -> Path:
        return self.__image_src_path

    @image_src_path.setter
    def image_src_path(self, image_src_path: Union[str, Path]) -> None:
        if not isinstance(image_src_path, Path):
            image_src_path = Path(image_src_path)
        if not image_src_path.exists() or not image_src_path.is_file():
            raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), str(image_src_path))
        self.__image_src_path = image_src_path

    def preprocess_image(self) -> np.ndarray:
        preprocessed_image_name = self.__ensure_grayscaled()
        preprocessed_image = cv2.imread(preprocessed_image_name, cv2.IMREAD_GRAYSCALE)
        preprocessed_image = self.__apply_thresh(preprocessed_image)
        return preprocessed_image

    def __ensure_grayscaled(self) -> str:
        temp_file = NamedTemporaryFile(delete=False, suffix='.tif', dir=self._temp_directory.name)
        with Image.open(self.image_src_path) as img:
            img.convert('L')
            img.save(temp_file.name)
        return temp_file.name

    def __apply_thresh(self, img: np.ndarray) -> np.ndarray:
        return cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

__all__ = ['AviTesseractImage']
