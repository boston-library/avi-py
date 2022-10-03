from __future__ import absolute_import
from __future__ import print_function
from __future__ import annotations

import os
import errno
import logging
import json
from pathlib import Path
from typing import Union
from PIL import Image
import numpy as np

import pytesseract

from . import constants as avi_const
from .avi_tesseract_image import AviTesseractImage

class AviTesseractProcessorError(Exception):
    pass

class AviTesseractProcessor:
    def __init__(self, image_src_path: [Union[str, Path]]) -> None:
        self.image_src_path = image_src_path
        self.success = False
        self.result_message = ''
        self.logger = logging.getLogger('avi_py')

    @classmethod
    def process(cls, image_src_path: Union[str, Path]) -> AviTesseractProcessor:
        tess_processsor = cls(image_src_path)
        tess_processsor.ocr_for_batch()
        return tess_processsor

    @property
    def image_src_path(self) -> Path:
        return self.__image_src_path

    @image_src_path.setter
    def image_src_path(self, image_src_path: Union[str, Path]) -> None:
        if not isinstance(image_src_path, Path):
            image_src_path = Path(image_src_path)
        if not image_src_path.exists() or not image_src_path.is_file():
            raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), str(image_src_path))
        self.__image_src_path = image_src_path

    @property
    def result(self) -> dict:
        return { 'success': self.success, 'message': self.result_message }

    def json_result(self) -> str:
        return json.dumps(self.result)

    def ocr_for_batch(self) -> None:
        try:
            self.logger.debug('Generating searchable PDF...')
            self.__generate_pdf()
            self.logger.debug('Generating mets/alto...')
            with AviTesseractImage(self.image_src_path) as pre_processed_img:
                self.__generate_mets_alto(pre_processed_img)
            self.__set_success_result()
        except AviTesseractProcessorError as avi_ex:
            self.logger.error('Error occured processing file for OCR!')
            self.logger.error(f'Reason {avi_ex}')
            self.__set_error_result(str(avi_ex))

    def __generate_pdf(self) -> None:
        try:
            pdf = pytesseract.image_to_pdf_or_hocr(str(self.image_src_path), extension=avi_const.TESS_OUT_FILE_TYPES['pdf'], lang=avi_const.TESS_DEFAULT_LANG, config=avi_const.TESS_DEFAULT_CFG)
            out_file_path = self.__out_file_path(avi_const.TESS_OUT_FILE_TYPES['pdf'])
            self.logger.debug(f'Outputting PDF file at {out_file_path}')
            self.__write_out_file(pdf, out_file_path)
        except Exception as ex:
            raise AviTesseractProcessorError(f'Error Occured during PDF generation! Reason {ex}')

    def __generate_mets_alto(self, pre_processed_img: np.nadarry) -> None:
        try:
            xml = pytesseract.image_to_alto_xml(Image.fromarray(pre_processed_img, mode='L'), lang=avi_const.TESS_DEFAULT_LANG, config=avi_const.TESS_DEFAULT_CFG)
            out_file_path = self.__out_file_path(avi_const.TESS_OUT_FILE_TYPES['alto'])
            self.logger.debug(f'Outputting Mets Alto Xml file at {out_file_path}')
            self.__write_out_file(xml, out_file_path)
        except Exception as ex:
            raise AviTesseractProcessorError(f'Error Occured during Mets alto generation! Reason {ex}')

    def __generate_bbox_data(self, pre_processed_img: np.ndarray) -> None:
        # TODO
        pass

    def __out_file_path(self, out_extension: str) -> Path:
        basename = self.image_src_path.stem
        directory = self.image_src_path.parent
        return directory / f'{basename}.{out_extension}'

    def __write_out_file(self, out_file_contents: Union[bytes, str], out_file_path: Path, binary: bool=True) -> None:
        fmode = 'w+'
        if binary:
            fmode = 'w+b'
        with open(out_file_path, fmode) as out_file:
            out_file.write(out_file_contents)

    def __set_success_result(self) -> None:
        self.success = True
        self.result_message = f'Successfully created OCR pdf/xml files at {self.image_src_path.parent}'

    def __set_error_result(self, error_msg: str='') -> None:
        self.success = False
        self.result_message = error_msg

__all__ = ['AviTesseractProcessor', 'AviTesseractProcessorError']
