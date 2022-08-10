import logging
import sys
from pathlib import Path

import pytest

from avi_py.avi_ffprobe_data import AviFFProbeData
from avi_py.avi_audio_data import AviAudioData
from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def get_audio_data(audio_src_path) -> AviAudioData:
    return AviAudioData(audio_src_path)

@pytest.fixture(name='wav_audio_data')
def fixture_wav_audio_data() -> AviAudioData:
    return get_audio_data(file_fixtures.WAV_AUDIO)


class TestAviAudioData:
    """
    Unit tests for the AviAudioData class
    """
    def test_wav_audio_data(self, wav_audio_data):
        assert bool(wav_audio_data) is True
        assert isinstance(wav_audio_data, AviAudioData)
        assert issubclass(wav_audio_data.__class__, AviFFProbeData)
        assert isinstance(wav_audio_data.audio_src_path, Path)

        assert str(wav_audio_data.audio_src_path) == file_fixtures.WAV_AUDIO

        assert isinstance(wav_audio_data.audio_ext, str)
        assert wav_audio_data.audio_ext == '.wav'
        assert wav_audio_data.valid_audio_ext() is True

        assert bool(wav_audio_data.ffmpeg_probe) is True
        assert isinstance(wav_audio_data.ffmpeg_probe, dict)

        for key in ['format', 'streams']:
            assert key in wav_audio_data.ffmpeg_probe.keys()

        assert bool(wav_audio_data.ffprobe_format) is True
        assert isinstance(wav_audio_data.ffprobe_format, dict)

        assert bool(wav_audio_data.ffprobe_streams) is True
        assert isinstance(wav_audio_data.ffprobe_streams, list)

        for stream in wav_audio_data.ffprobe_streams:
            assert bool(stream) is True
            assert isinstance(stream, dict)

        assert bool(wav_audio_data.audio_streams) is True
        assert isinstance(wav_audio_data.audio_streams, list)

        assert wav_audio_data.raw_stream is not None
        assert isinstance(wav_audio_data.raw_stream, dict)

        for audio_stream in wav_audio_data.audio_streams:
            assert bool(audio_stream) is True
            assert isinstance(audio_stream, dict)
