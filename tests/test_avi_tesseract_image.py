import logging
import sys
from pathlib import Path

import pytest

from avi_py.avi_tesseract_image import AviTesseractImage
from avi_py import constants as avi_const
from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
