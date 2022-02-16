import logging
import pytest
import os
import sys
import json

from tempfile import TemporaryDirectory, NamedTemporaryFile
from pathlib import Path
from image_processing import conversion
from image_processing.kakadu import Kakadu
from avi_py.avi_jp2_processor import AviJp2Processor
from avi_py.avi_image_data import AviImageData

from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@pytest.fixture(scope='module')
def temp_folder(prefix='avi_test_image_files', dir='/tmp'):
    temp_dir = TemporaryDirectory(prefix=prefix, dir=dir)
    print(f'Created temp file at {temp_dir.name}')
    yield temp_dir.name
    temp_dir.cleanup()

@pytest.fixture
def grayscaled_destination_file(temp_folder):
    dest_file = NamedTemporaryFile(dir=temp_folder, prefix='test-grayscaled-image',suffix='.jp2')
    print(f'Created temp file at {dest_file.name}')
    yield dest_file.name
    dest_file.close()

@pytest.fixture
def srgb_destination_file(temp_folder):
    dest_file = NamedTemporaryFile(dir=temp_folder, prefix='test-srgb-image',suffix='.jp2')
    print(f'Created temp file at {dest_file.name}')
    yield dest_file.name
    dest_file.close()

@pytest.fixture
def no_icc_destination_file(temp_folder):
    dest_file = NamedTemporaryFile(dir=temp_folder, prefix='test-no-icc-image',suffix='.jp2')
    print(f'Created temp file at {dest_file.name}')
    yield dest_file.name
    dest_file.close()

class TestAviJp2Convert:
    def test_grayscaled_image_convert(self, temp_folder, grayscaled_destination_file):
        grayscaled_image_convert = AviJp2Processor.process_jp2(file_fixtures.GRAYSCALED_IMAGE, destination_file=grayscaled_destination_file)

        assert isinstance(grayscaled_image_convert, AviJp2Processor)
        assert isinstance(grayscaled_image_convert.image_data, AviImageData)

        assert grayscaled_image_convert.destination_file == grayscaled_destination_file

        assert isinstance(grayscaled_image_convert.kakadu, Kakadu)
        assert isinstance(grayscaled_image_convert.converter, conversion.Converter)

        assert isinstance(grayscaled_image_convert.success, bool)

        assert isinstance(grayscaled_image_convert.result_message, str)
        assert isinstance(grayscaled_image_convert.result, dict)

        for key in ['success', 'message']:
            assert key in grayscaled_image_convert.result.keys()

        assert grayscaled_image_convert.success is True
        assert grayscaled_image_convert.success == grayscaled_image_convert.result.get('success')

        assert grayscaled_image_convert.result_message ==  f'Successfully converted and wrote file to {grayscaled_destination_file}'
        assert grayscaled_image_convert.result_message == grayscaled_image_convert.result.get('message')

        assert isinstance(grayscaled_image_convert.json_result(), str)
        assert grayscaled_image_convert.json_result() == json.dumps(grayscaled_image_convert.result)

    def test_srgb_image_convert(self, temp_folder, srgb_destination_file):
        srgb_image_convert = AviJp2Processor.process_jp2(file_fixtures.SRGB_IMAGE, srgb_destination_file)

        assert isinstance(srgb_image_convert, AviJp2Processor)
        assert isinstance(srgb_image_convert.image_data, AviImageData)

        assert srgb_image_convert.destination_file == srgb_destination_file

        assert isinstance(srgb_image_convert.kakadu, Kakadu)
        assert isinstance(srgb_image_convert.converter, conversion.Converter)

        assert isinstance(srgb_image_convert.success, bool)
        assert isinstance(srgb_image_convert.result_message, str)
        assert isinstance(srgb_image_convert.result, dict)

        for key in ['success', 'message']:
            assert key in srgb_image_convert.result.keys()

        assert srgb_image_convert.success is True
        assert srgb_image_convert.success == srgb_image_convert.result.get('success')

        assert srgb_image_convert.result_message ==  f'Successfully converted and wrote file to {srgb_destination_file}'
        assert srgb_image_convert.result_message == srgb_image_convert.result.get('message')

        assert isinstance(srgb_image_convert.json_result(), str)
        assert srgb_image_convert.json_result() == json.dumps(srgb_image_convert.result)

    def test_no_icc_image_convert(self, temp_folder, no_icc_destination_file):
        no_icc_image_convert = AviJp2Processor.process_jp2(file_fixtures.NO_ICC_IMAGE, no_icc_destination_file)

        assert isinstance(no_icc_image_convert, AviJp2Processor)
        assert isinstance(no_icc_image_convert.image_data, AviImageData)

        assert no_icc_image_convert.destination_file == no_icc_destination_file

        assert isinstance(no_icc_image_convert.kakadu, Kakadu)
        assert isinstance(no_icc_image_convert.converter, conversion.Converter)

        assert isinstance(no_icc_image_convert.success, bool)
        assert isinstance(no_icc_image_convert.result_message, str)
        assert isinstance(no_icc_image_convert.result, dict)

        for key in ['success', 'message']:
            assert key in no_icc_image_convert.result.keys()

        assert no_icc_image_convert.success is True
        assert no_icc_image_convert.success == no_icc_image_convert.result.get('success')

        assert no_icc_image_convert.result_message == f'Successfully converted and wrote file to {no_icc_destination_file}'
        assert no_icc_image_convert.result_message == no_icc_image_convert.result.get('message')

        assert isinstance(no_icc_image_convert.json_result(), str)
        assert no_icc_image_convert.json_result() == json.dumps(no_icc_image_convert.result)
