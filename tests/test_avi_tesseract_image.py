import logging
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import numpy as np

from PIL import Image
from avi_py.avi_tesseract_image import AviTesseractImage
from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@pytest.fixture(name='ocr_tesseract_image')
def fixture_ocr_tesseract_image() -> AviTesseractImage:
    return AviTesseractImage(file_fixtures.OCR_IMAGE)

@pytest.fixture(name='ocr_tesseract_image_ctx')
def fixture_ocr_tesseract_image_ctx():
    with AviTesseractImage(file_fixtures.OCR_IMAGE) as pre_processed_img:
        yield pre_processed_img

class TestAviTesseractImage:
    """
    Unit tests for the AviTesseractImage class
    """
    def test_avi_tesseract_image(self, ocr_tesseract_image):
        assert isinstance(ocr_tesseract_image, AviTesseractImage)
        assert isinstance(ocr_tesseract_image.image_src_path, Path)
        assert str(ocr_tesseract_image.image_src_path) == file_fixtures.OCR_IMAGE
        assert isinstance(ocr_tesseract_image._temp_directory, TemporaryDirectory)
        assert isinstance(ocr_tesseract_image.preprocess_image(), np.ndarray)

    def test_avi_tesseract_image_with_stmnt(self, ocr_tesseract_image_ctx):
        assert isinstance(ocr_tesseract_image_ctx, np.ndarray)
        tess_img = Image.fromarray(ocr_tesseract_image_ctx, mode='L')
        assert tess_img.mode == 'L'
