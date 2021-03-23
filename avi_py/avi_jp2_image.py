import tempfile
import shutil
import logging
import subprocess
import sys
import json
from pathlib import Path
from typing import Union
from image_processing.exceptions import KakaduError, ValidationError, ImageProcessingError
from image_processing import validation, kakadu, conversion
from image_processing.kakadu import Kakadu
from PIL import Image
from PIL.ImageCms import PyCMSError

from avi_py import constants as avi_const
from avi_py.avi_image_data import AviImageData


class AviJp2ImageError(Exception):
    pass

class AviJp2Image:
    def __init__(self, input_file_path: Union[str, Path],
                output_dir: Union[str, Path]=avi_const.DERIVATIVES_OUT_FOLDER,
                console_debug: bool=avi_const.CONSOLE_DEBUG_MODE) -> None:
        self.image_data = AviImageData(input_file_path)
        self.kakadu = Kakadu(kakadu_base_path=avi_const.KAKADU_BASE_PATH)
        self.converter = conversion.Converter(exiftool_path=avi_const.EXIFTOOL_PATH)
        self.output_dir = output_dir
        self.result = {}
        self.logger = logging.getLogger(__name__)
        if console_debug:
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(logging.StreamHandler(sys.stdout))

    @property
    def result(self) -> dict:
        return self._result

    @result.setter
    def result(self, res: dict) -> None:
        self._result = res

    @property
    def output_dir(self) -> str:
        return self._output_dir

    @output_dir.setter
    def output_dir(self, out_dir: Union[str, Path]) -> None:
        self._output_dir = str(out_dir)

    def json_result(self) -> str:
        return json.dumps(self.result)

    def convert_to_jp2(self) -> None:
        try:
            if not self.image_data.valid_image_ext():
                raise AviJp2ImageError('Source image is not a .tiff or .tif')

            kdu_args = self.__calculate_kdu_options() + self.__calculate_kdu_recipe()
            input_file = str(self.image_data.image_src_path)
            jp2_out_file = f'{self.output_dir}/{self.__get_out_filename(ext=".jp2")}'

            if self.image_data.src_quality == 'color':
                self.logger.debug('Adding icc profile to image')
                input_file = self.convert_icc_profile()
                self.logger.debug('Successfully added icc profile')

            self.logger.debug('Pre validating image at {}'.format(input_file))

            try:
                validation.check_image_suitable_for_jp2_conversion(
                    input_file, require_icc_profile_for_colour=True,
                    require_icc_profile_for_greyscale=False)
            except ValidationError as v_e:
                msg = f'ValidationError: {v_e}'
                self.__set_error_result(msg)
                raise AviJp2ImageError(msg)

            self.logger.debug('image {} is able to be converted to jp2!'.format(input_file))

            with Image.open(input_file) as input_pil:
                if input_pil.mode == 'RGBA':
                    if kakadu.ALPHA_OPTION not in kdu_args:
                        kdu_args += [kakadu.ALPHA_OPTION]

            self.logger.debug('Kakadu args are {}'.format(kdu_args))
            self.logger.debug('Preparing to output jp2...')

            try:
                self.kakadu.kdu_compress(input_file, jp2_out_file, kakadu_options=kdu_args)
            except (KakaduError, OSError) as kdu_e:
                msg = f'{kdu_e.__class__.__name__} {kdu_e}'
                self.__set_error_result(msg)
                raise AviJp2ImageError(msg)
            self.logger.debug('Successfully converted to jp2!')
            self.__set_success_result(jp2_out_file)
        except AviJp2ImageError:
            self.logger.error('Error Occured processing file check result to see details')

    def convert_icc_profile(self) -> str:
        try:
            out_file = f'{self.output_dir}/{self.__get_out_filename(ext=self.image_data.image_ext(), prefix="icc_converted_")}'
            with tempfile.NamedTemporaryFile(prefix='image-processing_', suffix=self.image_data.image_ext()) as temp_tiff_file_obj:
                temp_tiff_filepath = temp_tiff_file_obj.name
                shutil.copy(str(self.image_data.image_src_path), temp_tiff_filepath)
                if self.image_data.needs_icc_profile():
                    self.__convert_icc_profile_with_magick(temp_tiff_filepath, out_file)
                else:
                    self.logger.debug('Adding icc profile with pillow..')
                    self.converter.convert_icc_profile(temp_tiff_filepath, out_file, str(avi_const.ICC_PROFILE_PATH))
            return out_file
        except (AssertionError, PyCMSError, ImageProcessingError, IOError) as a_e:
            msg = f'{a_e.__class__.__name__}{a_e}'
            self.__set_error_result(msg)
            raise AviJp2ImageError(msg)

    def __convert_icc_profile_with_magick(self, input_file: str, out_file: str) -> None:
        assert shutil.which('convert') is not None, 'imagemagick not installed on this system!'

        icc_profile_path = str(avi_const.ICC_PROFILE_PATH)
        magick_commands = [
            'convert',
            '-quiet',
            input_file,
            '-profile', icc_profile_path,
            out_file
        ]
        self.logger.debug('Converting icc profile with the following imagemagick commands...')
        self.logger.debug(magick_commands)
        try:
            subprocess.call(magick_commands)
        except subprocess.CalledProcessError as sp_e:
            msg = f'ICC Magick Convert Failed!\n Reason: {sp_e}'
            raise IOError(msg)

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
