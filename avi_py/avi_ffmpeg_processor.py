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
from .avi_audio_data import AviAudioData

#pylint: disable=missing-class-docstring
class AviFFMpegProcessorError(Exception):
    pass
#pylint: enable=missing-class-docstring

class AviFFMpegProcessor:
    """
    Class that checks and converts a source video file thumbnail derivative
    """
    def __init__(self, src_file_path: Union[str, Path], dest_file_path: Union[str, Path], is_video: bool=True) -> None:
        self.success = False
        self.result_message = ''
        self.dest_file_path = dest_file_path
        if is_video:
            self.video_data = AviVideoData(src_file_path)
            self.audio_data = None
        else:
            self.audio_data = AviAudioData(src_file_path)
            self.video_data = None
        self.logger = logging.getLogger('avi_py')

    @classmethod
    def process_thumbnail(cls, src_file_path: Union[str, Path], dest_file_path: Union[str, Path], is_video: bool=True) -> AviFFMpegProcessor:
        ffmpeg_processor = cls(src_file_path, dest_file_path, is_video)
        ffmpeg_processor.generate_thumbnail()
        return ffmpeg_processor

    @classmethod
    def process_mp3(cls, src_file_path: Union[str, Path], dest_file_path: Union[str, Path], is_video: bool=False) -> AviFFMpegProcessor:
        ffmpeg_processor = cls(src_file_path, dest_file_path, is_video)
        ffmpeg_processor.generate_mp3()
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

    def generate_mp3(self) -> None:
        try:
            if self.audio_data is None:
                raise AviFFMpegProcessorError('Source Audio Data is None. Did you mean to call generate_mp3?')
            if not self.audio_data.valid_audio_ext():
                raise AviFFMpegProcessorError('Source audio is not a .wav')
            self._ffmpeg_mp3()
            self.__set_success_result()
        except AviFFMpegProcessorError as avi_ex:
            msg = str(avi_ex)
            self.__set_error_result(msg)
            self.logger.error('Error Occured processing file for ffmpeg audio mp3 derivative!')
            self.logger.error('Check result and logs to see additional details')

    def generate_thumbnail(self) -> None:
        try:
            if self.video_data is None:
                raise AviFFMpegProcessorError('Source Video Data is None. Did you mean to call generate_mp3?')
            if not self.video_data.valid_video_ext():
                raise AviFFMpegProcessorError('Source video is not a .mov or .mp4')
            with tempfile.NamedTemporaryFile(prefix='avi_py-ffmpeg-thumb_', suffix='.jpg') as ffmpeg_jpeg:
                self._ffmpeg_thumbnail(ffmpeg_jpeg.name)
            self.__set_success_result()
        except AviFFMpegProcessorError as avi_ex:
            msg = str(avi_ex)
            self.__set_error_result(msg)
            self.logger.error('Error Occured processing file for ffmpeg video thumbnail derivative!')
            self.logger.error('Check result and logs to see additional details')

    def _ffmpeg_thumbnail(self, out_file_path: str) -> None:
        try:
            self.__ffmpeg_downscale_screen_grab(out_file_path)
            with Image.open(out_file_path) as ffmpeg_jpg_frame:
                ffmpeg_jpg_frame.thumbnail(avi_const.FFMPEG_THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                ffmpeg_jpg_frame.save(self.dest_file_path)
        except ffmpeg.Error as ff_ex:
            msg = 'Ffmpeg Error! {}'.format(ff_ex.stderr.decode())
            raise AviFFMpegProcessorError(msg) from ff_ex
        except Exception as ex:
            msg = f'{ex.__class__.__name__} {ex}'
            raise AviFFMpegProcessorError(msg) from ex

    def _ffmpeg_mp3(self) -> None:
        try:
            ffmpeg \
                .input(str(self.audio_data.audio_src_path)) \
                .output(str(self.dest_file_path),**avi_const.FFMPEG_AUDIO_ARGS) \
                .overwrite_output() \
                .run(capture_stdout=avi_const.CONSOLE_DEBUG_MODE, capture_stderr=True)
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
        self.result_message = f'Successfully created ffmpeg derivative at {self.dest_file_path}'

    def __set_error_result(self, error_msg: str='') -> None:
        self.success = False
        self.result_message = error_msg

__all__ = ['AviFFMpegProcessor', 'AviFFMpegProcessorError']
