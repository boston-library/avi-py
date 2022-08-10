from pathlib import Path
from typing import Union, List

import ffmpeg

class AviFFProbeData:
    """
    Base Class for storing all low level audio/video data for functions that are used for
    creating audio/video deriavtives with ffprobe
    """
    def __init__(self, src_file_path: Union[str, Path]) -> None:
        self.ffmpeg_probe = ffmpeg.probe(src_file_path)

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

    # The following two properties should be included by default in inherited classes
    @property
    def raw_stream(self) -> dict:
        return next((stream for stream in self.ffprobe_streams if stream['codec_type'] == 'data'), {})

    # NOTE: More than one audio channel
    @property
    def audio_streams(self) -> List[dict]:
        return [stream for stream in self.ffprobe_streams if stream['codec_type'] == 'audio']

__all__ = ['AviFFProbeData']
