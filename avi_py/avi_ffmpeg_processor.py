from __future__ import absolute_import
from __future__ import print_function
from __future__ import annotations

import os
import errno

from typing import Union
from pathlib import Path

from PIL import Image
import ffmpeg
from . import constants as avi_const

class AviFFMpegProcessorError(Exception):
    pass

class AviFFMpegProcessor:
    def __init__(self, src_file_path: Union[str, Path], dest_file_path: Union[str, Path]) -> None:
        pass

    @classmethod
    def process_thumbnail(cls, src_file_path: Union[str, Path], dest_file_path: Union[str, Path]) -> AviFFMpegProcessor:
        pass
