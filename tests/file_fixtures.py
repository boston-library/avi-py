import errno
import os
import pytest

from pathlib import Path
from PIL import Image
from contextlib import contextmanager
from avi_py import constants as avi_const

TEST_FILE_DIR=avi_const.PROJECT_ROOT / 'tests' / 'data'
GRAYSCALED_IMAGE=str(TEST_FILE_DIR / 'grayscaled_image.tif')
NO_ICC_IMAGE=str(TEST_FILE_DIR / 'no_icc_profile_image.tif')
SRGB_IMAGE=str(TEST_FILE_DIR / 'srgb_image.tiff')

MP4_VIDEO=str(TEST_FILE_DIR / 'mlk.mp4')
MOV_VIDEO=str(TEST_FILE_DIR / 'mlk.mov')

WAV_AUDIO=str(TEST_FILE_DIR / 'audio-test.wav')

@contextmanager
def image_fixture(img_path):
    p = Path(str(img_path))
    if not p.is_file():
        raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), str(img_path))
    with Image.open(p) as img_fixture:
        yield img_fixture
