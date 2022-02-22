import os
import errno

from pathlib import Path
from typing import Union, List

import ffmpeg

from . import constants as avi_const

class AviVideoData:
    """
    Class for storing all low level video data for functions that are used for
    creating video deriavtives with FFMpeg
    """
    def __init__(self, video_src_path: Union[str, Path]) -> None:
        self.video_src_path = video_src_path
        self.ffmpeg_probe = ffmpeg.probe(video_src_path)

    @property
    def video_src_path(self) -> Path:
        return self.__video_src_path

    @video_src_path.setter
    def video_src_path(self, video_src_path: Union[str, Path]) -> None:
        if not isinstance(video_src_path, Path):
            video_src_path = Path(video_src_path)
        if not video_src_path.exists() or not video_src_path.is_file():
            raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), str(video_src_path))
        self.__video_src_path = video_src_path

    @property
    def ffmpeg_probe(self) -> dict:
        return self.__ffmpeg_probe

    @ffmpeg_probe.setter
    def ffmpeg_probe(self, ffprobe: dict) -> None:
        self.__ffmpeg_probe = ffprobe

    @property
    def ffprobe_streams(self) -> List[dict]:
        if 'streams' in self.ffmpeg_probe.keys():
            return self.ffmpeg_probe['streams']
        return []

    @property
    def ffprobe_format(self) -> dict:
        if 'format' in self.ffmpeg_probe.keys():
            return self.ffmpeg_probe['format']
        return {}

    @property
    def video_stream(self) -> dict:
        return next((stream for stream in self.ffprobe_streams if stream['codec_type'] == 'video'), {})

    # NOTE: More than one audio channel
    @property
    def audio_streams(self) -> List[dict]:
        return [stream for stream in self.ffprobe_streams if stream['codec_type'] == 'audio']

    @property
    def raw_stream(self) -> dict:
        return next((stream for stream in self.ffprobe_streams if stream['codec_type'] == 'data'), {})

    @property
    def video_ext(self) -> str:
        return self.video_src_path.suffix

    def valid_video_ext(self) -> bool:
        return self.video_ext in avi_const.VALID_VIDEO_EXTENSIONS

    def ss_time(self) -> int:
        if 'duration' not in self.ffprobe_format.keys():
            return avi_const.FFMPEG_DEFAULT_SS_TIME
        duration = float(self.ffprobe_format['duration'])
        screenshot_time = round(duration / 2)
        return int(screenshot_time)

__all__ = ['AviVideoData']
