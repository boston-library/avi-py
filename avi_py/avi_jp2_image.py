import tempfile
import shutil
import os
import logging
import errno
import subprocess
import sys

from .constants import *
from .avi_image_data import AviImageData

from pathlib import Path
from image_processing.exceptions import KakaduError
from image_processing import validation, kakadu, conversion
from image_processing.kakadu import Kakadu
from PIL import Image, ImageCms

class AviJp2Image:
    def __init__(self, input_file_path: str) -> None:
        self.image_data = AviImageData(input_file_path)
        self.kakadu = Kakadu(kakadu_base_path=KAKADU_BASE_PATH)
        self.converter = conversion.Converter(exiftool_path=EXIFTOOL_PATH)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def convert_to_jp2(self) -> str:
        kdu_args = self.__calculate_kdu_options() + self.__calculate_kdu_recipe()
        input_file = str(self.image_data.image_src_path)
        jp2_out_file = f'{DERIVATIVES_OUT_FOLDER}/{self.__get_out_filename(ext="jp2")}'

        if self.image_data.src_quality == 'color':
            self.logger.debug(f'Adding icc profile to image')
            input_file = self.convert_icc_profile()
            self.logger.debug(f'Successfully added icc profile')

        self.logger.debug(f'Pre validating image at {input_file}')

        validation.check_image_suitable_for_jp2_conversion(
            input_file, require_icc_profile_for_colour=True,
            require_icc_profile_for_greyscale=False)

        self.logger.debug(f'image {input_file} is able to be converted to jp2!')

        with Image.open(input_file) as input_pil:
            if input_pil.mode == 'RGBA':
                if kakadu.ALPHA_OPTION not in kdu_args:
                    kdu_args += [kakadu.ALPHA_OPTION]

        self.logger.debug(f'Kakadu args are {kdu_args}')
        self.logger.debug(f'Preparing to output jp2...')

        self.kakadu.kdu_compress(input_file, jp2_out_file, kakadu_options=kdu_args)
        self.logger.debug('successfully converted to jp2!')
        return jp2_out_file

    def convert_icc_profile(self) -> str:
        out_file = f'{DERIVATIVES_OUT_FOLDER}/{self.__get_out_filename(ext=self.image_data.image_ext(), prefix="icc_converted_")}'
        with tempfile.NamedTemporaryFile(prefix='image-processing_', suffix=self.image_data.image_ext()) as temp_tiff_file_obj:
            temp_tiff_filepath = temp_tiff_file_obj.name
            shutil.copy(str(self.image_data.image_src_path), temp_tiff_filepath)
            # if self.image_data.needs_icc_profile():
                #Going to have to call image magick in this case
                # with Image.open(temp_tiff_filepath) as tif_pil:
                #     tif_pil.convert('RGB')
                #     tif_pil.save(temp_tiff_filepath, compression='tiff_adobe_deflate')
            self.converter.convert_icc_profile(temp_tiff_filepath, out_file, ICC_PROFILE_PATH, new_colour_mode='RGB')
        return out_file

    def __calculate_kdu_recipe(self) -> list:
        return [
          "Stiles={" + self.image_data.tile_size + "}",
          f'Clevels={self.image_data.level_count_for_size()}',
          f'Clayers={KDU_DEFAULT_LAYER_COUNT}',
        ] + KAKADU_DEFAULT_RECIPE

    def __calculate_kdu_options(self) -> list:
        return [
                '-rate', f'{self.image_data.layer_rates()}',
                '-jp2_space', f'{self.image_data.jp2_space()}'
        ] + KAKADU_DEFAULT_OPTIONS

    def __get_out_filename(self, ext: str, prefix: str=''):
        return f'{prefix}{self.image_data.image_src_path.stem}.{ext}'
