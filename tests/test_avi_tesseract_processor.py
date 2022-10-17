import logging
import sys
import json
import shutil
from tempfile import TemporaryDirectory, NamedTemporaryFile
from pathlib import Path

import pytest

from avi_py import constants as avi_const
from avi_py.avi_tesseract_processor import AviTesseractProcessor

from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@pytest.fixture(scope='module', name='temp_folder')
def fixture_temp_folder():
    with TemporaryDirectory(prefix='avi_test_image_files', dir='/tmp') as temp_dir:
        print(f'Created temp file at {temp_dir}')
        yield temp_dir

@pytest.fixture(name='ocr_file')
def fixture_ocr_file(temp_folder):
    with NamedTemporaryFile(dir=temp_folder, prefix='test-ocr-image', suffix='.tif') as ocr_img:
        print(f'Created temp file at {ocr_img.name}')
        shutil.copy(file_fixtures.OCR_IMAGE, ocr_img.name)
        yield ocr_img.name

@pytest.fixture(name='avi_tesseract_processor')
def fixture_avi_tesseract_processor() -> AviTesseractProcessor:
    return AviTesseractProcessor(file_fixtures.OCR_IMAGE)


@pytest.fixture(name='processed_ocr')
def fixture_processed_ocr(ocr_file) -> AviTesseractProcessor:
    return AviTesseractProcessor.process_batch_ocr(ocr_file)

class TestAviTesseractProcessor:
    """
    Unit tests for the AviTesseractProcessor class
    """
    def test_avi_tesseract_processor(self, avi_tesseract_processor):
        assert isinstance(avi_tesseract_processor, AviTesseractProcessor)
        assert isinstance(avi_tesseract_processor.image_src_path, Path)
        assert isinstance(avi_tesseract_processor.tesseract_langs, str)
        assert isinstance(avi_tesseract_processor.tesseract_config, str)
        assert isinstance(avi_tesseract_processor.replace_if_exists, bool)
        assert isinstance(avi_tesseract_processor.success, bool)
        assert isinstance(avi_tesseract_processor.result_message, str)
        assert isinstance(avi_tesseract_processor.result, dict)
        assert isinstance(avi_tesseract_processor.json_result(), str)
        assert isinstance(avi_tesseract_processor.has_pdf(), bool)
        assert isinstance(avi_tesseract_processor.has_mets_alto(), bool)
        assert isinstance(avi_tesseract_processor.should_generate_pdf(), bool)
        assert isinstance(avi_tesseract_processor.should_generate_mets_alto(), bool)

        assert str(avi_tesseract_processor.image_src_path) == file_fixtures.OCR_IMAGE
        assert avi_tesseract_processor.tesseract_langs == avi_const.TESS_DEFAULT_LANG
        assert avi_tesseract_processor.tesseract_config == avi_const.TESS_DEFAULT_CFG
        assert avi_tesseract_processor.replace_if_exists is False
        assert avi_tesseract_processor.success is False
        assert avi_tesseract_processor.result_message == ''
        assert avi_tesseract_processor.result == { 'success': False, 'message': '' }
        assert avi_tesseract_processor.json_result() == json.dumps(avi_tesseract_processor.result)

    def test_process_batch_ocr(self, processed_ocr):
        assert isinstance(processed_ocr, AviTesseractProcessor)
        assert processed_ocr.success is True
        expected_result_message =  f'Successfully created OCR pdf/xml files at {processed_ocr.image_src_path.parent}'
        assert processed_ocr.result_message == expected_result_message
        assert processed_ocr.result == { 'success': True, 'message': expected_result_message }
        assert processed_ocr.json_result() == json.dumps({ 'success': True, 'message': expected_result_message })
        assert processed_ocr.has_pdf() is True
        assert processed_ocr.has_mets_alto() is True
