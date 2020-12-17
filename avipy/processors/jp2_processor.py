import logging
import os
import typing
import tempfile
from pathlib import Path
from image_processing.derivative_files_generator import DerivativeFilesGenerator
from image_processing.exceptions import ValidationError, ImageProcessingError, KakaduError
from from image_processing import kakadu, validation
from .processor_constants import KAKADU_BASE_PATH

class JP2Processor:
    def self.__init__(self, source_file_path: Path) -> None:
        self.__source_file_path = source_file_path

    @property
    def source_file_path(self) -> Path:
        return self.__source_file_path

    def output_file_path(self): -> Path:
        pass

    def check_if_valid_image(self) -> None:
        validation.check_image_suitable_for_jp2_conversion(str(self.source_file_path()))

    def generate_tmp_file(self) -> Path:
        pass

    def convert_to_jp2(self):
        try:
            self.check_if_valid_image()
            generator = DerivativeFilesGenerator(kakadu_base_path=KAKADU_BASE_PATH,
                                                 kakadu_compress_options=kakadu.DEFAULT_LOSSLESS_COMPRESS_OPTIONS)
            out_file_path = self.output_file_path()
            self.generate_tmp_file()
            derivatives_gen.generate_jp2_from_tiff(str(self.source_file_path()),str(out_file_path))
            derivatives_gen.validate_jp2_conversion(str(self.source_file_path()), str(out_file_path) check_lossless=True)
            return str(out_file_path)
        except ValidationError as err:
            # Delete file out tmp file if exists
            logger.exception(f'Validation Error Occured! {err.message}')
