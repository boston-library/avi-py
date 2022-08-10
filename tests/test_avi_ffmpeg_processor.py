import logging
import sys
import json
from tempfile import TemporaryDirectory, NamedTemporaryFile

import pytest

from avi_py.avi_video_data import AviVideoData
from avi_py.avi_audio_data import AviAudioData
from avi_py.avi_ffmpeg_processor import AviFFMpegProcessor

from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@pytest.fixture(scope='module', name='temp_folder')
def fixture_temp_folder():
    with TemporaryDirectory(prefix='avi_test_video_files', dir='/tmp') as temp_dir:
        print(f'Created temp file at {temp_dir}')
        yield temp_dir

@pytest.fixture(name='thumbnail_dest_file')
def fixture_thumbnail_dest_file(temp_folder):
    with NamedTemporaryFile(dir=temp_folder, prefix='test-thumbnail-out', suffix='.jpg') as dest_file:
        print(f'Created temp file at {dest_file.name}')
        yield dest_file.name


@pytest.fixture(name='mp3_destination_file')
def fixture_mp3_destination_file(temp_folder):
    with NamedTemporaryFile(dir=temp_folder, prefix='test-mp3-out', suffix='.mp3') as dest_file:
        print(f'Created temp file at {dest_file.name}')
        yield dest_file.name


class TestAviFFMpegProcessor:
    """
    Tests for processing mp3s and thumbnails for the AviFFMpegProcessor class
    """
    def test_mov_thumbnail_generation(self, thumbnail_dest_file):
        mov_ffmpeg_thumbnail = AviFFMpegProcessor.process_thumbnail(file_fixtures.MOV_VIDEO, thumbnail_dest_file)

        assert isinstance(mov_ffmpeg_thumbnail, AviFFMpegProcessor)
        assert isinstance(mov_ffmpeg_thumbnail.success, bool)
        assert isinstance(mov_ffmpeg_thumbnail.result_message, str)
        assert isinstance(mov_ffmpeg_thumbnail.dest_file_path, str)
        assert isinstance(mov_ffmpeg_thumbnail.result, dict)
        assert isinstance(mov_ffmpeg_thumbnail.json_result(), str)
        assert isinstance(mov_ffmpeg_thumbnail.video_data, AviVideoData)

        assert mov_ffmpeg_thumbnail.audio_data is None
        assert mov_ffmpeg_thumbnail.dest_file_path == thumbnail_dest_file
        assert mov_ffmpeg_thumbnail.success is True
        assert mov_ffmpeg_thumbnail.result_message == f'Successfully created ffmpeg derivative at {thumbnail_dest_file}'

        assert bool(mov_ffmpeg_thumbnail.result) is True
        assert all(key in mov_ffmpeg_thumbnail.result for key in ['success', 'message'])
        assert mov_ffmpeg_thumbnail.success == mov_ffmpeg_thumbnail.result.get('success')
        assert mov_ffmpeg_thumbnail.result_message == mov_ffmpeg_thumbnail.result.get('message')

        assert mov_ffmpeg_thumbnail.json_result() == json.dumps(mov_ffmpeg_thumbnail.result)

        with file_fixtures.image_fixture(thumbnail_dest_file) as mov_jpg:
            assert mov_jpg.format =='JPEG'
            assert mov_jpg.width == 300

    def test_mp4_thumbnail_generation(self, thumbnail_dest_file):
        mp4_ffmpeg_thumbnail = AviFFMpegProcessor.process_thumbnail(file_fixtures.MP4_VIDEO, thumbnail_dest_file)

        assert isinstance(mp4_ffmpeg_thumbnail, AviFFMpegProcessor)
        assert isinstance(mp4_ffmpeg_thumbnail.success, bool)
        assert isinstance(mp4_ffmpeg_thumbnail.result_message, str)
        assert isinstance(mp4_ffmpeg_thumbnail.dest_file_path, str)
        assert isinstance(mp4_ffmpeg_thumbnail.result, dict)
        assert isinstance(mp4_ffmpeg_thumbnail.json_result(), str)
        assert isinstance(mp4_ffmpeg_thumbnail.video_data, AviVideoData)

        assert mp4_ffmpeg_thumbnail.audio_data is None
        assert mp4_ffmpeg_thumbnail.dest_file_path == thumbnail_dest_file
        assert mp4_ffmpeg_thumbnail.success is True
        assert mp4_ffmpeg_thumbnail.result_message == f'Successfully created ffmpeg derivative at {thumbnail_dest_file}'

        assert bool(mp4_ffmpeg_thumbnail.result) is True
        assert all(key in mp4_ffmpeg_thumbnail.result for key in ['success', 'message'])

        assert mp4_ffmpeg_thumbnail.success == mp4_ffmpeg_thumbnail.result.get('success')
        assert mp4_ffmpeg_thumbnail.result_message == mp4_ffmpeg_thumbnail.result.get('message')

        assert mp4_ffmpeg_thumbnail.json_result() == json.dumps(mp4_ffmpeg_thumbnail.result)

        with file_fixtures.image_fixture(thumbnail_dest_file) as mp4_jpg:
            assert mp4_jpg.format =='JPEG'
            assert mp4_jpg.width == 300

    def test_wav_mp3_generation(self, mp3_destination_file):
        wav_ffmpeg_mp3 = AviFFMpegProcessor.process_mp3(file_fixtures.WAV_AUDIO, mp3_destination_file)

        assert isinstance(wav_ffmpeg_mp3, AviFFMpegProcessor)
        assert isinstance(wav_ffmpeg_mp3.success, bool)
        assert isinstance(wav_ffmpeg_mp3.result_message, str)
        assert isinstance(wav_ffmpeg_mp3.dest_file_path, str)
        assert isinstance(wav_ffmpeg_mp3.result, dict)
        assert isinstance(wav_ffmpeg_mp3.json_result(), str)
        assert isinstance(wav_ffmpeg_mp3.audio_data, AviAudioData)

        assert wav_ffmpeg_mp3.video_data is None
        assert wav_ffmpeg_mp3.dest_file_path == mp3_destination_file
        assert wav_ffmpeg_mp3.success is True
        assert wav_ffmpeg_mp3.result_message == f'Successfully created ffmpeg derivative at {mp3_destination_file}'

        assert bool(wav_ffmpeg_mp3.result) is True
        assert all(key in wav_ffmpeg_mp3.result for key in ['success', 'message'])
        assert wav_ffmpeg_mp3.success == wav_ffmpeg_mp3.result.get('success')
        assert wav_ffmpeg_mp3.result_message == wav_ffmpeg_mp3.result.get('message')

        assert wav_ffmpeg_mp3.json_result() == json.dumps(wav_ffmpeg_mp3.result)
