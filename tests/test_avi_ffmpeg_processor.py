import logging
import pytest
import os
import sys
import json

from tempfile import TemporaryDirectory, NamedTemporaryFile
from pathlib import Path

from avi_py.avi_video_data import AviVideoData
from avi_py.avi_ffmpeg_processor import AviFFMpegProcessor

from . import file_fixtures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@pytest.fixture(scope='module')
def temp_folder(prefix='avi_test_video_files', dir='/tmp'):
    temp_dir = TemporaryDirectory(prefix=prefix, dir=dir)
    print(f'Created temp file at {temp_dir.name}')
    yield temp_dir.name
    temp_dir.cleanup()

@pytest.fixture
def thumbnail_dest_file(temp_folder):
    dest_file = NamedTemporaryFile(dir=temp_folder, prefix='test-thumbnail-out',suffix='.jpg')
    print(f'Created temp file at {dest_file.name}')
    yield dest_file.name
    dest_file.close()


class TestAviFFMpegProcessor:
    def test_mov_thumbnail(self, temp_folder, thumbnail_dest_file):
        mov_ffmpeg_thumbnail = AviFFMpegProcessor.process_thumbnail(file_fixtures.MOV_VIDEO, thumbnail_dest_file)

        assert isinstance(mov_ffmpeg_thumbnail, AviFFMpegProcessor)
        assert isinstance(mov_ffmpeg_thumbnail.success, bool)
        assert isinstance(mov_ffmpeg_thumbnail.result_message, str)
        assert isinstance(mov_ffmpeg_thumbnail.video_data, AviVideoData)
        assert isinstance(mov_ffmpeg_thumbnail.dest_file_path, str)
        assert isinstance(mov_ffmpeg_thumbnail.result, dict)
        assert isinstance(mov_ffmpeg_thumbnail.json_result(), str)

        assert mov_ffmpeg_thumbnail.dest_file_path == thumbnail_dest_file
        assert mov_ffmpeg_thumbnail.success is True
        assert mov_ffmpeg_thumbnail.result_message == f'Successfully created thumbnail at {thumbnail_dest_file}'

        assert bool(mov_ffmpeg_thumbnail.result) is True
        for key in ['success', 'message']:
            assert key in mov_ffmpeg_thumbnail.result.keys()

        assert mov_ffmpeg_thumbnail.success == mov_ffmpeg_thumbnail.result.get('success')
        assert mov_ffmpeg_thumbnail.result_message == mov_ffmpeg_thumbnail.result.get('message')

        assert mov_ffmpeg_thumbnail.json_result() == json.dumps(mov_ffmpeg_thumbnail.result)

        with file_fixtures.image_fixture(thumbnail_dest_file) as mov_jpg:
            assert mov_jpg.format =='JPEG'
            assert mov_jpg.width == 300

    def test_mp4_thumbnail(self, temp_folder, thumbnail_dest_file):
        mp4_ffmpeg_thumbnail = AviFFMpegProcessor.process_thumbnail(file_fixtures.MP4_VIDEO, thumbnail_dest_file)

        assert isinstance(mp4_ffmpeg_thumbnail, AviFFMpegProcessor)
        assert isinstance(mp4_ffmpeg_thumbnail.success, bool)
        assert isinstance(mp4_ffmpeg_thumbnail.result_message, str)
        assert isinstance(mp4_ffmpeg_thumbnail.video_data, AviVideoData)
        assert isinstance(mp4_ffmpeg_thumbnail.dest_file_path, str)
        assert isinstance(mp4_ffmpeg_thumbnail.result, dict)
        assert isinstance(mp4_ffmpeg_thumbnail.json_result(), str)
        assert mp4_ffmpeg_thumbnail.dest_file_path == thumbnail_dest_file
        assert mp4_ffmpeg_thumbnail.success is True
        assert mp4_ffmpeg_thumbnail.result_message == f'Successfully created thumbnail at {thumbnail_dest_file}'

        assert bool(mp4_ffmpeg_thumbnail.result) is True
        for key in ['success', 'message']:
            assert key in mp4_ffmpeg_thumbnail.result.keys()

        assert mp4_ffmpeg_thumbnail.success == mp4_ffmpeg_thumbnail.result.get('success')
        assert mp4_ffmpeg_thumbnail.result_message == mp4_ffmpeg_thumbnail.result.get('message')

        assert mp4_ffmpeg_thumbnail.json_result() == json.dumps(mp4_ffmpeg_thumbnail.result)

        with file_fixtures.image_fixture(thumbnail_dest_file) as mp4_jpg:
            assert mp4_jpg.format =='JPEG'
            assert mp4_jpg.width == 300