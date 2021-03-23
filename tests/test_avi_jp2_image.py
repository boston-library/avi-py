import logging
import pytest
import os
import sys
import json

from tempfile import TemporaryDirectory
from pathlib import Path
from image_processing import conversion
from image_processing.kakadu import Kakadu
from avi_py.avi_jp2_image import AviJp2Image
from avi_py.avi_image_data import AviImageData

from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@pytest.fixture(scope='module')
def temp_folder(prefix='avi_test_files', dir='/tmp'):
    temp_dir = TemporaryDirectory(prefix=prefix, dir=dir)
    print(f'Created temp dir at {temp_dir.name}')
    yield temp_dir.name
    temp_dir.cleanup()

class TestAviJp2Image:
    def test_grayscaled_image_convert(self, temp_folder):
        grayscaled_image_convert = AviJp2Image(input_file_path=file_fixtures.GRAYSCALED_IMAGE, output_dir=temp_folder, console_debug=False)

        assert isinstance(grayscaled_image_convert, AviJp2Image)
        assert isinstance(grayscaled_image_convert.image_data, AviImageData)

        assert grayscaled_image_convert.output_dir == temp_folder

        assert isinstance(grayscaled_image_convert.kakadu, Kakadu)
        assert isinstance(grayscaled_image_convert.converter, conversion.Converter)

        assert isinstance(grayscaled_image_convert.result, dict)
        assert grayscaled_image_convert.result == {}

        grayscaled_image_convert.convert_to_jp2()
        for key in ['success', 'jp2_file_path']:
            assert key in grayscaled_image_convert.result.keys()

        assert isinstance(grayscaled_image_convert.result.get('success'), bool)
        assert grayscaled_image_convert.result.get('success') == True

        assert isinstance(grayscaled_image_convert.result.get('jp2_file_path'), str)
        assert grayscaled_image_convert.result.get('jp2_file_path') == f'{temp_folder}/grayscaled_image.jp2'

        assert isinstance(grayscaled_image_convert.json_result(), str)
        assert grayscaled_image_convert.json_result() == json.dumps(grayscaled_image_convert.result)

    def test_srgb_image_convert(self, temp_folder):
        srgb_image_convert = AviJp2Image(input_file_path=file_fixtures.SRGB_IMAGE, output_dir=temp_folder, console_debug=False)

        assert isinstance(srgb_image_convert, AviJp2Image)
        assert isinstance(srgb_image_convert.image_data, AviImageData)

        assert srgb_image_convert.output_dir == temp_folder

        assert isinstance(srgb_image_convert.kakadu, Kakadu)
        assert isinstance(srgb_image_convert.converter, conversion.Converter)

        assert isinstance(srgb_image_convert.result, dict)
        assert srgb_image_convert.result == {}

        srgb_image_convert.convert_to_jp2()
        for key in ['success', 'jp2_file_path']:
            assert key in srgb_image_convert.result.keys()

        assert isinstance(srgb_image_convert.result.get('success'), bool)
        assert srgb_image_convert.result.get('success') == True

        assert isinstance(srgb_image_convert.result.get('jp2_file_path'), str)
        assert srgb_image_convert.result.get('jp2_file_path') == f'{temp_folder}/srgb_image.jp2'

        assert isinstance(srgb_image_convert.json_result(), str)
        assert srgb_image_convert.json_result() == json.dumps(srgb_image_convert.result)

    def test_no_icc_image_convert(self, temp_folder):
        no_icc_image_convert = AviJp2Image(input_file_path=file_fixtures.NO_ICC_IMAGE, output_dir=temp_folder, console_debug=False)

        assert isinstance(no_icc_image_convert, AviJp2Image)
        assert isinstance(no_icc_image_convert.image_data, AviImageData)

        assert no_icc_image_convert.output_dir == temp_folder

        assert isinstance(no_icc_image_convert.kakadu, Kakadu)
        assert isinstance(no_icc_image_convert.converter, conversion.Converter)

        assert isinstance(no_icc_image_convert.result, dict)
        assert no_icc_image_convert.result == {}

        no_icc_image_convert.convert_to_jp2()
        for key in ['success', 'jp2_file_path']:
            assert key in no_icc_image_convert.result.keys()

        assert isinstance(no_icc_image_convert.result.get('success'), bool)
        assert no_icc_image_convert.result.get('success') == True

        assert isinstance(no_icc_image_convert.result.get('jp2_file_path'), str)
        assert no_icc_image_convert.result.get('jp2_file_path') == f'{temp_folder}/no_icc_profile_image.jp2'

        assert isinstance(no_icc_image_convert.json_result(), str)
        assert no_icc_image_convert.json_result() == json.dumps(no_icc_image_convert.result)
