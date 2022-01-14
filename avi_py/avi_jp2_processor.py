from __future__ import absolute_import
from __future__ import print_function
from __future__ import annotations

import tempfile
import shutil
import logging
import subprocess
import json
import os
from pathlib import Path
from typing import Union
from image_processing.exceptions import KakaduError, ValidationError, ImageProcessingError
from image_processing import validation, kakadu
from image_processing.conversion import Converter
from image_processing.kakadu import Kakadu
from PIL import Image
from PIL.ImageCms import PyCMSError
from . import constants as avi_const
from .avi_image_data import AviImageData

#pylint: disable=unnecessary-pass
class AviJp2ProcessorError(Exception):
    """
    Top level Avi jp2 processor exception class
    """
    pass
#pylint: enable=unnecessary-pass

class AviConverter(Converter):
    """
    Overloaded class for coversion that allows exiftool to be run in quiet mode
    """
    def __init__(self, exiftool_path='exiftool', quiet=False):
        super().__init__(exiftool_path)
        self.quiet = quiet
#pylint: disable=raise-missing-from
    def copy_over_embedded_metadata(self, input_image_filepath, output_image_filepath, write_only_xmp=False):
        """
        Copy embedded image metadata from the input_image_filepath to the output_image_filepath
        :param input_image_filepath: input filepath
        :param output_image_filepath: output filepath
        :param write_only_xmp: Copy all information to the same-named tags in XMP (if they exist). With JP2 it's safest to only use xmp tags, as other ones may not be supported by all software
        """
        if not os.access(input_image_filepath, os.R_OK):
            raise IOError("Could not read input image path {0}".format(input_image_filepath))
        if not os.access(output_image_filepath, os.W_OK):
            raise IOError("Could not write to output path {0}".format(output_image_filepath))

        command_options = [self.exiftool_path]
        if self.quiet:
            command_options += ['-q']
        command_options += ['-tagsFromFile', input_image_filepath, '-overwrite_original']
        if write_only_xmp:
            command_options += ['-xmp:all<all']
        command_options += [output_image_filepath]
        self.logger.debug(' '.join(command_options))
        try:
            subprocess.check_call(command_options, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            raise ImageProcessingError('Exiftool at {0} failed to copy from {1}. Command: {2}, Error: {3}'.
                                       format(self.exiftool_path, input_image_filepath, ' '.join(command_options), error))
#pylint: enable=raise-missing-from


class AviJp2Processor:
    """
    Class that checks and converts a source tiff image to a jp2 derivative
    """
    def __init__(self, input_file_path: Union[str, Path], destination_file: Union[str, Path]) -> None:
        self.image_data = AviImageData(input_file_path)
        self.kakadu = Kakadu(kakadu_base_path=avi_const.KAKADU_BASE_PATH)
        self.converter = AviConverter(exiftool_path=avi_const.EXIFTOOL_PATH, quiet=not avi_const.CONSOLE_DEBUG_MODE)
        self.destination_file = destination_file
        self.success = True
        self.result_message = ''
        self.logger = logging.getLogger('avi_py')

    @classmethod
    def process_jp2(cls, input_file_path: Union[str, Path], destination_file: Union[str, Path]) -> AviJp2Processor:
        jp2_converter = cls(input_file_path, destination_file)
        jp2_converter.convert_to_jp2()
        return jp2_converter

    def result(self) -> dict:
        return { 'success': self.success, 'message': self.result_message }

    @property
    def success(self) -> bool:
        return self.__success

    @success.setter
    def success(self, new_success: bool) -> None:
        self.__success = new_success

    @property
    def result_message(self) -> str:
        return self.__result_message

    @result_message.setter
    def result_message(self, message: str) -> None:
        self.__result_message = message

    @property
    def destination_file(self) -> str:
        return self.__destination_file

    @destination_file.setter
    def destination_file(self, destination_file: Union[str, Path]) -> None:
        self.__destination_file = str(destination_file)

    def json_result(self) -> str:
        return json.dumps(self.result())

    def convert_to_jp2(self) -> None:
        try:
            if not self.image_data.valid_image_ext():
                raise AviJp2ProcessorError('Source image is not a .tiff or .tif')

            kdu_args = self.__calculate_kdu_options() + self.__calculate_kdu_recipe()
            input_file = str(self.image_data.image_src_path)

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
                raise AviJp2ProcessorError(msg) from v_e

            self.logger.debug('image {} is able to be converted to jp2!'.format(input_file))

            with Image.open(input_file) as input_pil:
                if input_pil.mode == 'RGBA':
                    if kakadu.ALPHA_OPTION not in kdu_args:
                        kdu_args += [kakadu.ALPHA_OPTION]

            self.logger.debug('Kakadu args are {}'.format(kdu_args))
            self.logger.debug('Preparing to output jp2...')
            try:
                self.kakadu.kdu_compress(input_file, self.destination_file, kakadu_options=kdu_args)
            except (KakaduError, OSError) as kdu_e:
                msg = f'{kdu_e.__class__.__name__} {kdu_e}'
                self.__set_error_result(msg)
                raise AviJp2ProcessorError(msg) from kdu_e
            self.logger.debug('Successfully converted to jp2!')
            self.__set_success_result()
        except AviJp2ProcessorError:
            self.logger.error('Error Occured processing file check result to see details')

    def convert_icc_profile(self) -> str:
        try:
            #pylint: disable=consider-using-with
            out_file = tempfile.NamedTemporaryFile(prefix='image_processing-icc-convert-out', suffix=self.image_data.image_ext(), delete=False)
            #pylint: enable=consider-using-with
            with tempfile.NamedTemporaryFile(prefix='image-processing_', suffix=self.image_data.image_ext()) as temp_tiff_file_obj:
                temp_tiff_filepath = temp_tiff_file_obj.name
                shutil.copy(str(self.image_data.image_src_path), temp_tiff_filepath)
                if self.image_data.needs_icc_profile():
                    self.__convert_icc_profile_with_magick(temp_tiff_filepath, out_file.name)
                else:
                    self.logger.debug('Adding icc profile with pillow..')
                    self.converter.convert_icc_profile(temp_tiff_filepath, out_file.name, str(avi_const.ICC_PROFILE_PATH))
            return out_file.name
        except (AssertionError, PyCMSError, ImageProcessingError, IOError) as a_e:
            msg = f'{a_e.__class__.__name__}{a_e}'
            self.__set_error_result(msg)
            raise AviJp2ProcessorError(msg) from a_e

    def __convert_icc_profile_with_magick(self, input_file: str, out_file: str) -> None:
        assert shutil.which('convert') is not None, 'imagemagick not installed on this system!'

        icc_profile_path = str(avi_const.ICC_PROFILE_PATH)
        magick_commands = avi_const.MAGICK_DEFAULT_CONVERT_COMMANDS.copy()
        magick_commands.extend([input_file, '-profile', icc_profile_path, out_file])
        self.logger.debug('Converting icc profile with the following imagemagick commands...')
        self.logger.debug(magick_commands)
        try:
            subprocess.call(magick_commands)
        except subprocess.CalledProcessError as sp_e:
            msg = f'ICC Magick Convert Failed!\n Reason: {sp_e}'
            raise IOError(msg) from sp_e

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

    def __set_success_result(self) -> None:
        self.success = True
        self.result_message = f'Successfully converted and wrote file to {self.destination_file}'

    def __set_error_result(self, error_msg: str='') -> None:
        self.logger.error(error_msg)
        self.success = False
        self.result_message = error_msg

__all__ = ['AviJp2Processor', 'AviJp2ProcessorError', 'AviConverter']
