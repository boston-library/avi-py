from __future__ import absolute_import
from __future__ import print_function
from __future__ import annotations

import os
import json
import logging
import ffmpeg

from typing import Union
from pathlib import Path
from PIL import Image

from . import constants as avi_const
from .avi_video_data import AviVideoData

#pylint: disable=missing-class-docstring
class AviFFMpegProcessorError(Exception):
    pass
#pylint: enable=missing-class-docstring

class AviFFMpegProcessor:
    def __init__(self, src_file_path: Union[str, Path], dest_file_path: Union[str, Path]) -> None:
        self.video_data = AviVideoData(src_file_path)
        self.success = True
        self.result_message = ''
        self.logger = logging.getLogger('avi_py')

    @classmethod
    def process_thumbnail(cls, src_file_path: Union[str, Path], dest_file_path: Union[str, Path]) -> AviFFMpegProcessor:
        pass

    @property
    def result_message(self) -> str:
        return self.__result_message

    @result_message.setter
    def result_message(self, message: str) -> None:
        self.__result_message = message

    @property
    def result(self) -> dict:
        return { 'success': self.success, 'message': self.result_message }

    @property
    def dest_file_path(self) -> str:
        return self.__dest_file_path

    @dest_file_path.setter
    def dest_file_path(self, dest_file_path: Union[str, Path]) -> None:
        if isinstance(dest_file_path, Path):
            dest_file_path = str(dest_file_path)
        self.__dest_file_path = dest_file_path

    def json_result(self) -> str:
        return json.dumps(self.result)

    def process_thumbnail(self) -> None:
        try:
            if not self.video_data.valid_video_ext():
                raise AviFFMpegProcessorError('Source video is not a .mov or .mp4')
            self.__ffmpeg_thumbnail()
        except AviFFMpegProcessorError as avi_ex:
            self.logger.error('Error Occured processing file for ffmpeg thumbnail!')
            self.logger.error('Details: {}'.format(str(avi_ex)))
            self.logger.error('Check result and logs to see additional details')

    def __ffmpeg_thumbnail(self) -> None:
        try:
            pass
        except ffmpeg.Error as ff_ex:
            pass
