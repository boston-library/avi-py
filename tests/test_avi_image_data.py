import logging
import pytest
import tempfile
import os
import sys
from pathlib import Path

from avi_py.avi_image_data import AviImageData
from avi_py import constants as avi_const
from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def get_image_data(image_path):
    return AviImageData(image_path)

@pytest.fixture
def grayscaled_image_data():
    return get_image_data(file_fixtures.GRAYSCALED_IMAGE)

@pytest.fixture
def srgb_image_data():
    return get_image_data(file_fixtures.SRGB_IMAGE)

@pytest.fixture
def no_icc_profile_image():
    return get_image_data(file_fixtures.NO_ICC_IMAGE)

class TestAviImageData:
    def test_grayscaled_image_data(self, grayscaled_image_data):
        assert isinstance(grayscaled_image_data, AviImageData)

        assert isinstance(grayscaled_image_data.image_src_path, Path)
        assert str(grayscaled_image_data.image_src_path) == file_fixtures.GRAYSCALED_IMAGE

        assert isinstance(grayscaled_image_data.tile_size, str)
        assert grayscaled_image_data.tile_size == f'{avi_const.KDU_DEFAULT_TILE_SIZE},{avi_const.KDU_DEFAULT_TILE_SIZE}'

        assert isinstance(grayscaled_image_data.src_quality, str)
        assert grayscaled_image_data.src_quality == 'gray'

        assert isinstance(grayscaled_image_data.layer_count, int)
        assert grayscaled_image_data.layer_count == avi_const.KDU_DEFAULT_LAYER_COUNT

        assert isinstance(grayscaled_image_data.compression_numerator, int)
        assert grayscaled_image_data.compression_numerator == avi_const.IMAGE_DEFAULT_COMPRESSION

        assert isinstance(grayscaled_image_data.image_ext(), str)
        assert grayscaled_image_data.image_ext() == '.tif'

        assert isinstance(grayscaled_image_data.valid_image_ext(), bool)
        assert grayscaled_image_data.valid_image_ext() == True

        assert isinstance(grayscaled_image_data.jp2_space(), str)
        assert grayscaled_image_data.jp2_space() == 'sLUM'

        assert isinstance(grayscaled_image_data.needs_icc_profile(), bool)
        assert grayscaled_image_data.needs_icc_profile() == False

    def test_srgb_image_data(self, srgb_image_data):
        assert isinstance(srgb_image_data, AviImageData)

        assert isinstance(srgb_image_data.image_src_path, Path)
        assert str(srgb_image_data.image_src_path) == file_fixtures.SRGB_IMAGE

        assert isinstance(srgb_image_data.tile_size, str)
        assert srgb_image_data.tile_size == f'{avi_const.KDU_DEFAULT_TILE_SIZE},{avi_const.KDU_DEFAULT_TILE_SIZE}'

        assert isinstance(srgb_image_data.src_quality, str)
        assert srgb_image_data.src_quality == 'color'

        assert isinstance(srgb_image_data.layer_count, int)
        assert srgb_image_data.layer_count == avi_const.KDU_DEFAULT_LAYER_COUNT

        assert isinstance(srgb_image_data.compression_numerator, int)
        assert srgb_image_data.compression_numerator == avi_const.IMAGE_DEFAULT_COMPRESSION

        assert isinstance(srgb_image_data.image_ext(), str)
        assert srgb_image_data.image_ext() == '.tiff'

        assert isinstance(srgb_image_data.valid_image_ext(), bool)
        assert srgb_image_data.valid_image_ext() == True

        assert isinstance(srgb_image_data.jp2_space(), str)
        assert srgb_image_data.jp2_space() == 'sRGB'

        assert isinstance(srgb_image_data.needs_icc_profile(), bool)
        assert srgb_image_data.needs_icc_profile() == False

    def test_no_icc_image_data(self, no_icc_profile_image):
        assert isinstance(no_icc_profile_image, AviImageData)

        assert isinstance(no_icc_profile_image.image_src_path, Path)
        assert str(no_icc_profile_image.image_src_path) == file_fixtures.NO_ICC_IMAGE

        assert isinstance(no_icc_profile_image.tile_size, str)
        assert no_icc_profile_image.tile_size == f'{avi_const.KDU_DEFAULT_TILE_SIZE},{avi_const.KDU_DEFAULT_TILE_SIZE}'

        assert isinstance(no_icc_profile_image.src_quality, str)
        assert no_icc_profile_image.src_quality == 'color'

        assert isinstance(no_icc_profile_image.layer_count, int)
        assert no_icc_profile_image.layer_count == avi_const.KDU_DEFAULT_LAYER_COUNT

        assert isinstance(no_icc_profile_image.compression_numerator, int)
        assert no_icc_profile_image.compression_numerator == avi_const.IMAGE_DEFAULT_COMPRESSION

        assert isinstance(no_icc_profile_image.image_ext(), str)
        assert no_icc_profile_image.image_ext() == '.tif'

        assert isinstance(no_icc_profile_image.valid_image_ext(), bool)
        assert no_icc_profile_image.valid_image_ext() == True

        assert isinstance(no_icc_profile_image.jp2_space(), str)
        assert no_icc_profile_image.jp2_space() == 'sRGB'

        assert isinstance(no_icc_profile_image.needs_icc_profile(), bool)
        assert no_icc_profile_image.needs_icc_profile() == True
