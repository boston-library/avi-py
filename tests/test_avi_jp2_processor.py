import logging
import sys
import json
from tempfile import TemporaryDirectory, NamedTemporaryFile

import pytest

from image_processing import conversion
from image_processing.kakadu import Kakadu
from avi_py.avi_jp2_processor import AviJp2Processor
from avi_py.avi_image_data import AviImageData

from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@pytest.fixture(scope='module', name='temp_folder')
def fixture_temp_folder():
    with TemporaryDirectory(prefix='avi_test_image_files', dir='/tmp') as temp_dir:
        print(f'Created temp file at {temp_dir}')
        yield temp_dir

@pytest.fixture(name='grayscaled_destination_file')
def fixture_grayscaled_destination_file(temp_folder):
    with NamedTemporaryFile(dir=temp_folder, prefix='test-grayscaled-image', suffix='.jp2') as dest_file:
        print(f'Created temp file at {dest_file.name}')
        yield dest_file.name

@pytest.fixture(name='srgb_destination_file')
def fixture_srgb_destination_file(temp_folder):
    with NamedTemporaryFile(dir=temp_folder, prefix='test-srgb-image', suffix='.jp2') as dest_file:
        print(f'Created temp file at {dest_file.name}')
        yield dest_file.name

@pytest.fixture(name='no_icc_destination_file')
def fixture_no_icc_destination_file(temp_folder):
    with NamedTemporaryFile(dir=temp_folder, prefix='test-no-icc-image', suffix='.jp2') as dest_file:
        print(f'Created temp file at {dest_file.name}')
        yield dest_file.name

class TestAviJp2Convert:
    """
    Tests for processing various tiffs to jp2s AviJp2Processor class
    """
    def test_grayscaled_image_convert(self, grayscaled_destination_file):
        grayscaled_image_convert = AviJp2Processor.process_jp2(file_fixtures.GRAYSCALED_IMAGE, destination_file=grayscaled_destination_file)

        assert isinstance(grayscaled_image_convert, AviJp2Processor)
        assert isinstance(grayscaled_image_convert.image_data, AviImageData)

        assert grayscaled_image_convert.destination_file == grayscaled_destination_file

        assert isinstance(grayscaled_image_convert.kakadu, Kakadu)
        assert isinstance(grayscaled_image_convert.converter, conversion.Converter)

        assert isinstance(grayscaled_image_convert.success, bool)

        assert isinstance(grayscaled_image_convert.result_message, str)
        assert isinstance(grayscaled_image_convert.result, dict)

        assert all(key in grayscaled_image_convert.result for key in ['success', 'message'])

        assert grayscaled_image_convert.success is True
        assert grayscaled_image_convert.success == grayscaled_image_convert.result.get('success')

        assert grayscaled_image_convert.result_message ==  f'Successfully converted and wrote file to {grayscaled_destination_file}'
        assert grayscaled_image_convert.result_message == grayscaled_image_convert.result.get('message')

        assert isinstance(grayscaled_image_convert.json_result(), str)
        assert grayscaled_image_convert.json_result() == json.dumps(grayscaled_image_convert.result)

    def test_srgb_image_convert(self, srgb_destination_file):
        srgb_image_convert = AviJp2Processor.process_jp2(file_fixtures.SRGB_IMAGE, srgb_destination_file)

        assert isinstance(srgb_image_convert, AviJp2Processor)
        assert isinstance(srgb_image_convert.image_data, AviImageData)

        assert srgb_image_convert.destination_file == srgb_destination_file

        assert isinstance(srgb_image_convert.kakadu, Kakadu)
        assert isinstance(srgb_image_convert.converter, conversion.Converter)

        assert isinstance(srgb_image_convert.success, bool)
        assert isinstance(srgb_image_convert.result_message, str)
        assert isinstance(srgb_image_convert.result, dict)

        assert all(key in srgb_image_convert.result for key in ['success', 'message'])

        assert srgb_image_convert.success is True
        assert srgb_image_convert.success == srgb_image_convert.result.get('success')

        assert srgb_image_convert.result_message ==  f'Successfully converted and wrote file to {srgb_destination_file}'
        assert srgb_image_convert.result_message == srgb_image_convert.result.get('message')

        assert isinstance(srgb_image_convert.json_result(), str)
        assert srgb_image_convert.json_result() == json.dumps(srgb_image_convert.result)

    def test_no_icc_image_convert(self, no_icc_destination_file):
        no_icc_image_convert = AviJp2Processor.process_jp2(file_fixtures.NO_ICC_IMAGE, no_icc_destination_file)

        assert isinstance(no_icc_image_convert, AviJp2Processor)
        assert isinstance(no_icc_image_convert.image_data, AviImageData)

        assert no_icc_image_convert.destination_file == no_icc_destination_file

        assert isinstance(no_icc_image_convert.kakadu, Kakadu)
        assert isinstance(no_icc_image_convert.converter, conversion.Converter)

        assert isinstance(no_icc_image_convert.success, bool)
        assert isinstance(no_icc_image_convert.result_message, str)
        assert isinstance(no_icc_image_convert.result, dict)

        assert all(key in no_icc_image_convert.result for key in ['success', 'message'])

        assert no_icc_image_convert.success is True
        assert no_icc_image_convert.success == no_icc_image_convert.result.get('success')

        assert no_icc_image_convert.result_message == f'Successfully converted and wrote file to {no_icc_destination_file}'
        assert no_icc_image_convert.result_message == no_icc_image_convert.result.get('message')

        assert isinstance(no_icc_image_convert.json_result(), str)
        assert no_icc_image_convert.json_result() == json.dumps(no_icc_image_convert.result)
