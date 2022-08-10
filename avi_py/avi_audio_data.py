import os
import errno

from pathlib import Path
from typing import Union, List

from . import constants as avi_const
from .avi_ffprobe_data import AviFFProbeData

class AviAudioData(AviFFProbeData):
    """
    Class for storing all low level video data for functions that are used for
    creating video deriavtives with FFMpeg
    """
    def __init__(self, audio_src_path: Union[str, Path]) -> None:
        self.audio_src_path = audio_src_path
        super().__init__(audio_src_path)

    @property
    def audio_src_path(self) -> Path:
        return self.__audio_src_path

    @audio_src_path.setter
    def audio_src_path(self, audio_src_path: Union[str, Path]) -> None:
        if not isinstance(audio_src_path, Path):
            audio_src_path = Path(audio_src_path)
        if not audio_src_path.exists() or not audio_src_path.is_file():
            raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), str(audio_src_path))
        self.__audio_src_path = audio_src_path

    @property
    def audio_streams(self) -> List[dict]:
        return [stream for stream in self.ffprobe_streams if stream['codec_type'] == 'audio']

    @property
    def audio_ext(self) -> str:
        return self.audio_src_path.suffix

    def valid_audio_ext(self) -> bool:
        return self.audio_ext in avi_const.VALID_AUDIO_EXTENSIONS

__all__ = ['AviAudioData']
