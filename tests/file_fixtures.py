import errno
import os
from pathlib import Path
from avi_py import constants as avi_const
from PIL import Image
import pytest

TEST_IMAGE_FILE_DIR=avi_const.PROJECT_ROOT / 'tests' / 'data'
GRAYSCALED_IMAGE=str(TEST_IMAGE_FILE_DIR / 'grayscaled_image.tif')
NO_ICC_IMAGE=str(TEST_IMAGE_FILE_DIR / 'no_icc_profile_image.tif')
SRGB_IMAGE=str(TEST_IMAGE_FILE_DIR / 'srgb_image.tiff')


@pytest.fixture
def image_fixture(img_path):
    p = Path(str(img_path))
    if not p.is_file():
        raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), str(img_path))
    with Image.open(p) as img_fixture:
        yield img_fixture
