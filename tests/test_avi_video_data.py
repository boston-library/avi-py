import logging
import pytest
import os
import sys
from pathlib import Path

from avi_py.avi_video_data import AviVideoData
from avi_py import constants as avi_const
from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def get_video_data(video_src_path) -> AviVideoData:
    return AviVideoData(video_src_path)

@pytest.fixture
def mov_video_data() -> AviVideoData:
    return AviVideoData(file_fixtures.MOV_VIDEO)

@pytest.fixture
def mp4_video_data() -> AviVideoData:
    return AviVideoData(file_fixtures.MP4_VIDEO)

class TestAviImageData:
    def test_mov_video_data(self, mov_video_data):
        assert isinstance(mov_video_data, AviVideoData)
        assert isinstance(mov_video_data.video_src_path, Path)

        assert str(mov_video_data.video_src_path) == file_fixtures.MOV_VIDEO

        assert isinstance(mov_video_data.video_ext, str)
        assert mov_video_data.video_ext == '.mov'
        assert mov_video_data.valid_video_ext() is True

        assert isinstance(mov_video_data.ffmpeg_probe, dict)
        assert bool(mov_video_data.ffmpeg_probe) is True

        for key in ['format', 'streams']:
            assert key in mov_video_data.ffmpeg_probe.keys()

        assert isinstance(mov_video_data.ffprobe_format, dict)
        assert bool(mov_video_data.ffprobe_format) is True

        assert isinstance(mov_video_data.ffprobe_streams, list)
        assert bool(mov_video_data) is True

        for stream in mov_video_data.ffprobe_streams:
            assert isinstance(stream, dict)
            assert bool(dict) is True

        assert isinstance(mov_video_data.video_stream, dict)
        assert bool(mov_video_data.video_stream) is True

        assert isinstance(mov_video_data.audio_streams, list)
        assert bool(mov_video_data.audio_streams) is True

        assert isinstance(mov_video_data.raw_stream, dict)
        assert bool(mov_video_data.raw_stream) is True

        for audio_stream in mov_video_data.audio_streams:
            assert isinstance(audio_stream, dict)
            assert bool(audio_stream) is True
        assert isinstance(mov_video_data.ss_time(), int)

    def test_mp4_video_datat(self, mp4_video_data):
        assert isinstance(mp4_video_data, AviVideoData)
        assert isinstance(mp4_video_data.video_src_path, Path)

        assert str(mp4_video_data.video_src_path) == file_fixtures.MP4_VIDEO

        assert isinstance(mp4_video_data.video_ext, str)
        assert mp4_video_data.video_ext == '.mp4'
        assert mp4_video_data.valid_video_ext() is True

        assert isinstance(mp4_video_data.ffmpeg_probe, dict)
        assert bool(mp4_video_data.ffmpeg_probe) is True

        for key in ['format', 'streams']:
            assert key in mp4_video_data.ffmpeg_probe.keys()

        assert isinstance(mp4_video_data.ffprobe_format, dict)
        assert bool(mp4_video_data.ffprobe_format) is True

        assert isinstance(mp4_video_data.ffprobe_streams, list)
        assert bool(mp4_video_data) is True

        for stream in mp4_video_data.ffprobe_streams:
            assert isinstance(stream, dict)
            assert bool(dict) is True

        assert isinstance(mp4_video_data.video_stream, dict)
        assert bool(mp4_video_data.video_stream) is True

        assert isinstance(mp4_video_data.audio_streams, list)
        assert bool(mp4_video_data.audio_streams) is True

        assert isinstance(mp4_video_data.raw_stream, dict)
        assert bool(mp4_video_data.raw_stream) is True

        for audio_stream in mp4_video_data.audio_streams:
            assert isinstance(audio_stream, dict)
            assert bool(audio_stream) is True
        assert isinstance(mp4_video_data.ss_time(), int)