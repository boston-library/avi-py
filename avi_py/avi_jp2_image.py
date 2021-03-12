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
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    @property
    def result(self) -> dict:
        return self._result

    @result.setter
    def result(self, res: dict={}) -> None:
        self._result = res

    def convert_to_jp2(self) -> str:
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
            self.logger.error(f'ValidationError: {ve}')
            exit(1)

        self.logger.debug(f'image {input_file} is able to be converted to jp2!')

        with Image.open(input_file) as input_pil:
            if input_pil.mode == 'RGBA':
                if kakadu.ALPHA_OPTION not in kdu_args:
                    kdu_args += [kakadu.ALPHA_OPTION]

        self.logger.debug(f'Kakadu args are {kdu_args}')
        self.logger.debug(f'Preparing to output jp2...')

        self.kakadu.kdu_compress(input_file, jp2_out_file, kakadu_options=kdu_args)
        self.logger.debug('Successfully converted to jp2!')
        return jp2_out_file

    def convert_icc_profile(self) -> str:
        out_file = f'{avi_const.DERIVATIVES_OUT_FOLDER}/{self.__get_out_filename(ext=self.image_data.image_ext(), prefix="icc_converted_")}'
        with tempfile.NamedTemporaryFile(prefix='image-processing_', suffix=self.image_data.image_ext()) as temp_tiff_file_obj:
            temp_tiff_filepath = temp_tiff_file_obj.name
            shutil.copy(str(self.image_data.image_src_path), temp_tiff_filepath)
            if self.image_data.needs_icc_profile():
                self.logger.debug("Adding default srgb profile..")
                temp_tiff_filepath = self.__convert_and_add_srgb_profile(temp_tiff_filepath)
                self.logger.debug("Profile added...")
                with Image.open(temp_tiff_filepath) as temp_pil:
                    self.logger.debug(f'{temp_pil.info}')
            self.converter.convert_icc_profile(temp_tiff_filepath, out_file, str(avi_const.ICC_PROFILE_PATH))
        return out_file

    def __convert_and_add_srgb_profile(self, temp_tiff_filepath: str) -> str:
        if not self.image_data.needs_icc_profile():
            return

        out_file = f'{avi_const.DERIVATIVES_OUT_FOLDER}/{self.__get_out_filename(ext=self.image_data.image_ext(), prefix="srgb_converted_")}'
        srgb_profile = ImageCms.createProfile('sRGB')
        with tempfile.NamedTemporaryFile(prefix='image-processing_', suffix=self.image_data.image_ext()) as tiff_rgb_out:
            temp_srgb_filepath = tiff_rgb_out.name
            shutil.copy(temp_tiff_filepath, temp_srgb_filepath)
            with Image.open(temp_srgb_filepath) as tiff_pil:
                tiff_pil.convert('RGB').save(out_file, icc_profile=srgb_profile, compression=tiff_pil.info.get('compression', 'tiff_lzw'))
        return out_file

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

    def __get_out_filename(self, ext: str, prefix: str=''):
        return f'{prefix}{self.image_data.image_src_path.stem}{ext}'
