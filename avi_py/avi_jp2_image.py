import tempfile
import shutil
import os
import logging
import errno
import subprocess
import sys
import json

from avi_py import constants as avi_const
from avi_py.avi_image_data import AviImageData

from pathlib import Path
from image_processing.exceptions import KakaduError, ValidationError
from image_processing import validation, kakadu, conversion
from image_processing.kakadu import Kakadu
from PIL import Image, ImageCms

class AviJp2Image:
    def __init__(self, input_file_path: str) -> None:
        self.image_data = AviImageData(input_file_path)
        self.kakadu = Kakadu(kakadu_base_path=avi_const.KAKADU_BASE_PATH)
        self.converter = conversion.Converter(exiftool_path=avi_const.EXIFTOOL_PATH)
        self.result = {}
        self.logger = logging.getLogger(__name__)
        if avi_const.DEBUG_MODE:
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(logging.StreamHandler(sys.stdout))
        else:
            self.logger.setLevel(logging.INFO)

    @property
    def result(self) -> dict:
        return self._result

    @result.setter
    def result(self, res: dict={}) -> None:
        self._result = res

    def json_result(self) -> str:
        return json.dumps(self.result)

    def convert_to_jp2(self) -> None:
        kdu_args = self.__calculate_kdu_options() + self.__calculate_kdu_recipe()
        input_file = str(self.image_data.image_src_path)
        jp2_out_file = f'{avi_const.DERIVATIVES_OUT_FOLDER}/{self.__get_out_filename(ext=".jp2")}'

        if self.image_data.src_quality == 'color':
            self.logger.debug(f'Adding icc profile to image')
            input_file = self.convert_icc_profile()
            self.logger.debug(f'Successfully added icc profile')

        self.logger.debug(f'Pre validating image at {input_file}')

        try:
            validation.check_image_suitable_for_jp2_conversion(
                input_file, require_icc_profile_for_colour=True,
                require_icc_profile_for_greyscale=False)
        except ValidationError as ve:
            msg = f'ValidationError: {ve}'
            self.__set_error_result(msg)
            sys.exit(self.json_result())

        self.logger.debug(f'image {input_file} is able to be converted to jp2!')

        with Image.open(input_file) as input_pil:
            if input_pil.mode == 'RGBA':
                if kakadu.ALPHA_OPTION not in kdu_args:
                    kdu_args += [kakadu.ALPHA_OPTION]

        self.logger.debug(f'Kakadu args are {kdu_args}')
        self.logger.debug(f'Preparing to output jp2...')

        self.kakadu.kdu_compress(input_file, jp2_out_file, kakadu_options=kdu_args)
        self.logger.debug('Successfully converted to jp2!')
        self.__set_success_result(jp2_out_file)

    def convert_icc_profile(self) -> str:
        try:
            out_file = f'{avi_const.DERIVATIVES_OUT_FOLDER}/{self.__get_out_filename(ext=self.image_data.image_ext(), prefix="icc_converted_")}'
            with tempfile.NamedTemporaryFile(prefix='image-processing_', suffix=self.image_data.image_ext()) as temp_tiff_file_obj:
                temp_tiff_filepath = temp_tiff_file_obj.name
                shutil.copy(str(self.image_data.image_src_path), temp_tiff_filepath)
                if self.image_data.needs_icc_profile():
                    self.__convert_icc_profile_with_magick(temp_tiff_filepath, out_file)
                else:
                    self.logger.debug('Adding icc profile with pillow..')
                    self.converter.convert_icc_profile(temp_tiff_filepath, out_file, str(avi_const.ICC_PROFILE_PATH))
            return out_file
        except AssertionError as ae:
            msg = f'{ae}'
            self.__set_error_result(msg)
            sys.exit(self.json_result())

    def __convert_icc_profile_with_magick(self, input_file: str, out_file: str) -> None:
        assert shutil.which('convert') is not None, 'imagemagick not installed on this system!'

        icc_profile_path = str(avi_const.ICC_PROFILE_PATH)
        magick_commands = [
            'convert',
            input_file,
            '-profile', icc_profile_path,
            out_file
        ]
        self.logger.debug('Converting icc profile with the following imagemagick commands...')
        self.logger.debug(magick_commands)
        try:
            subprocess.call(magick_commands)
        except subprocess.CalledProcessError as spe:
            msg = f'ICC Magick Convert Failed!\n Reason: {spe}'
            self.__set_error_result(msg)
            sys.exit(self.json_result())

    def __calculate_kdu_recipe(self) -> list:
        return [
          "Stiles={" + self.image_data.tile_size + "}",
          f'Clevels={self.image_data.level_count_for_size()}',
          f'Clayers={avi_const.KDU_DEFAULT_LAYER_COUNT}',
        ] + avi_const.KAKADU_DEFAULT_RECIPE

    def __calculate_kdu_options(self) -> list:
        return [
                '-rate', f'{self.image_data.layer_rates()}',
                '-jp2_space', f'{self.image_data.jp2_space()}'
        ] + avi_const.KAKADU_DEFAULT_OPTIONS

    def __get_out_filename(self, ext: str, prefix: str='') -> str:
        return f'{prefix}{self.image_data.image_src_path.stem}{ext}'

    def __set_success_result(self, jp2_file_path: str) -> None:
        self.result = {'success': True, 'jp2_file_path': jp2_file_path}

    def __set_error_result(self, error_msg: str='') -> None:
        self.logger.error(error_msg)
        self.result = {'success': False, 'error_msg': error_msg}
