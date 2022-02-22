from __future__ import absolute_import
from __future__ import print_function
from __future__ import annotations

import json
import tempfile
import logging
from typing import Union
from pathlib import Path

import ffmpeg

from PIL import Image

from . import constants as avi_const
from .avi_video_data import AviVideoData

#pylint: disable=missing-class-docstring
class AviFFMpegProcessorError(Exception):
    pass
#pylint: enable=missing-class-docstring

class AviFFMpegProcessor:
    """
    Class that checks and converts a source video file thumbnail derivative
    """
    def __init__(self, src_file_path: Union[str, Path], dest_file_path: Union[str, Path]) -> None:
        self.success = False
        self.result_message = ''
        self.dest_file_path = dest_file_path
        self.video_data = AviVideoData(src_file_path)
        self.logger = logging.getLogger('avi_py')

    @classmethod
    def process_thumbnail(cls, src_file_path: Union[str, Path], dest_file_path: Union[str, Path]) -> AviFFMpegProcessor:
        ffmpeg_processor = cls(src_file_path, dest_file_path)
        ffmpeg_processor.generate_thumbnail()
        return ffmpeg_processor

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

    def generate_thumbnail(self) -> None:
        try:
            if not self.video_data.valid_video_ext():
                raise AviFFMpegProcessorError('Source video is not a .mov or .mp4')
            with tempfile.NamedTemporaryFile(prefix='avi_py-ffmpeg-thumb_', suffix='.jpg') as ffmpeg_jpeg:
                self._ffmpeg_thumbnail(ffmpeg_jpeg.name)
            self.__set_success_result()
        except AviFFMpegProcessorError as avi_ex:
            msg = str(avi_ex)
            self.__set_error_result(msg)
            self.logger.error('Error Occured processing file for ffmpeg thumbnail!')
            self.logger.error('Check result and logs to see additional details')

    def _ffmpeg_thumbnail(self, out_file_path: str) -> None:
        try:
            self.__ffmpeg_downscale_screen_grab(out_file_path)
            with Image.open(out_file_path) as ffmpeg_jpg_frame:
                ffmpeg_jpg_frame.thumbnail(avi_const.FFMPEG_THUMBNAIL_SIZE, Image.LANCZOS)
                ffmpeg_jpg_frame.save(self.dest_file_path)
        except ffmpeg.Error as ff_ex:
            msg = 'Ffmpeg Error! {}'.format(ff_ex.stderr.decode())
            raise AviFFMpegProcessorError(msg) from ff_ex
        except Exception as ex:
            msg = f'{ex.__class__.__name__} {ex}'
            raise AviFFMpegProcessorError(msg) from ex

    def __ffmpeg_downscale_screen_grab(self, out_file_path: str) -> None:
        ffmpeg \
        .input(str(self.video_data.video_src_path), ss=self.video_data.ss_time()) \
        .filter('scale', -1, 360, force_original_aspect_ratio='decrease') \
        .output(out_file_path, vframes=1, vcodec='mjpeg') \
        .overwrite_output() \
        .run(capture_stdout=avi_const.CONSOLE_DEBUG_MODE, capture_stderr=True)

    def __set_success_result(self) -> None:
        self.success = True
        self.result_message = f'Successfully created thumbnail at {self.dest_file_path}'

    def __set_error_result(self, error_msg: str='') -> None:
        self.success = False
        self.result_message = error_msg

__all__ = ['AviFFMpegProcessor', 'AviFFMpegProcessorError']
