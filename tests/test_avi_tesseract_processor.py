import logging
import sys
import json
from tempfile import TemporaryDirectory, NamedTemporaryFile

from avi_py.avi_tesseract_image import AviTesseractImage
from avi_py.avi_tesseract_processor import AviTesseractProcessor

from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
