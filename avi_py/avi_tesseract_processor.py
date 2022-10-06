from __future__ import absolute_import
from __future__ import print_function
from __future__ import annotations

import os
import errno
import logging
import json
from pathlib import Path
from typing import Union
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image
import pytesseract
from . import constants as avi_const
from .avi_tesseract_image import AviTesseractImage

class AviTesseractProcessorError(Exception):
    pass


def _out_file_path(image_src_path: Path, out_extension: str) -> Path:
    basename = image_src_path.stem
    directory = image_src_path.parent
    return directory / f'{basename}.{out_extension}'

def _write_out_file(out_file_contents: Union[bytes, str], out_file_path: Path, binary: bool=True) -> None:
    fmode = 'w+'
    if binary:
        fmode = 'w+b'
    with open(out_file_path, fmode) as out_file:
        out_file.write(out_file_contents)

def generate_pdf(image_src_path: Union[Path, str], tess_langs: str, tess_cfg: str) -> None:
    try:
        pdf = pytesseract.image_to_pdf_or_hocr(str(image_src_path), extension=avi_const.TESS_OUT_FILE_TYPES['pdf'], lang=tess_langs, config=tess_cfg)
        out_file_path = _out_file_path(image_src_path, avi_const.TESS_OUT_FILE_TYPES['pdf'])
        _write_out_file(pdf, out_file_path)
    except Exception as ex:
        msg = f'Error ocurred during PDF gneration! Details: {ex.__class__.__name__}{ex}'
        raise AviTesseractProcessorError(msg) from ex

def generate_mets_alto(image_src_path: Union[Path, str], tess_langs: str, tess_cfg: str) -> None:
    try:
        with AviTesseractImage(image_src_path) as pre_processed_img:
            xml = pytesseract.image_to_alto_xml(Image.fromarray(pre_processed_img, mode='L'), lang=tess_langs, config=tess_cfg)
            out_file_path = _out_file_path(image_src_path, avi_const.TESS_OUT_FILE_TYPES['alto'])
            _write_out_file(xml, out_file_path)
    except Exception as ex:
        msg = f'Error ocurred during Mets alto gneration! Details: {ex.__class__.__name__}{ex}'
        raise AviTesseractProcessorError(msg) from ex

# TODO
# def generate_bbox_data(image_src_path: Path, tess_langs: str, tess_cfg: str) -> None:
#     pass

class AviTesseractProcessor:
    logger = logging.getLogger('avi_py')

    def __init__(self, image_src_path: Union[str, Path],
                       tess_langs: str=avi_const.TESS_DEFAULT_LANG,
                       tess_cfg: str=avi_const.TESS_DEFAULT_CFG,
                       replace_if_exists: bool=False) -> None:
        self.image_src_path = image_src_path
        self.tesseract_langs = tess_langs
        self.tesseract_config = tess_cfg
        self.replace_if_exists = replace_if_exists
        self.success = False
        self.result_message = ''

    @classmethod
    def process_batch_ocr(cls, image_src_path: Union[str, Path],
                               tess_langs: str=avi_const.TESS_DEFAULT_LANG,
                               tess_cfg: str=avi_const.TESS_DEFAULT_CFG,
                               replace_if_exists: bool=False) -> AviTesseractProcessor:
        tess_processsor = cls(image_src_path, tess_langs, tess_cfg, replace_if_exists)
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
        assert image_src_path.suffix == '.tif', f'source image: {image_src_path} is not a .tif file!'
        self.__image_src_path = image_src_path

    @property
    def tesseract_langs(self) -> str:
        return self.__tesseract_langs

    @tesseract_langs.setter
    def tesseract_langs(self, tess_langs: str) -> None:
        existing_langs = set(pytesseract.get_languages())
        langs = set(tess_langs.split('+'))
        assert langs.issubset(existing_langs), f'{tess_langs} are not valid tesseract languages'
        self.__tesseract_langs = tess_langs

    @property
    def tesseract_config(self) -> str:
        return self.__tesseract_config

    @tesseract_config.setter
    def tesseract_config(self, tess_cfg: str) -> None:
        self.__tesseract_config = tess_cfg

    @property
    def replace_if_exists(self) -> bool:
        return self.__replace_if_exists

    @replace_if_exists.setter
    def replace_if_exists(self, replace_if_exists: bool) -> None:
        self.__replace_if_exists = replace_if_exists

    @property
    def result(self) -> dict:
        return { 'success': self.success, 'message': self.result_message }

    def json_result(self) -> str:
        return json.dumps(self.result)

    def has_pdf(self) -> bool:
        expected_pdf_path = self.image_src_path.parent / f'{self.image_src_path.stem}.pdf'
        return expected_pdf_path.exists()

    def has_mets_alto(self) -> bool:
        expected_alto_path = self.image_src_path.parent / f'{self.image_src_path.stem}.xml'
        return expected_alto_path.exists()

    def should_generate_pdf(self) -> bool:
        if self.replace_if_exists:
            return True
        return not self.has_pdf()

    def should_generate_mets_alto(self) -> bool:
        if self.replace_if_exists:
            return True
        return not self.has_mets_alto()

    def ocr_for_batch(self) -> None:
        try:
            if not self.should_generate_pdf() and not self.should_generate_mets_alto():
                msg = f'OCR files already generated for {self.image_src_path}. Add replace_if_exists = True to replace them'
                self.__set_success_result(msg)
                return
            self._generate_ocr_files()
            self.__set_success_result()
        except AviTesseractProcessorError as avi_ex:
            self.__class__.logger.error('Error occured processing file for OCR!')
            self.__class__.logger.error(f'Reason {avi_ex}')
            self.__set_error_result(str(avi_ex))

    def _generate_ocr_files(self) -> None:
        with ProcessPoolExecutor(max_workers=2) as ocr_executor:
            try:
                process_list = []
                if self.should_generate_pdf():
                    process_list.append(ocr_executor.submit(generate_pdf, self.image_src_path, self.tesseract_langs, self.tesseract_config))
                if self.should_generate_mets_alto():
                    process_list.append(ocr_executor.submit(generate_mets_alto, self.image_src_path, self.tesseract_langs, self.tesseract_config))
                for process in as_completed(process_list):
                    process.result()
            except AviTesseractProcessorError as avi_ex:
                raise avi_ex
            except Exception as ex:
                msg = f'Error ocurred during OCR generation! Details: {ex.__class__.__name__}{ex}'
                raise AviTesseractProcessorError(msg) from ex

    def __set_success_result(self, msg: str=None) -> None:
        if msg is None:
            msg = f'Successfully created OCR pdf/xml files at {self.image_src_path.parent}'
        self.success = True
        self.result_message = msg

    def __set_error_result(self, error_msg: str='') -> None:
        self.success = False
        self.result_message = error_msg

__all__ = ['AviTesseractProcessor', 'AviTesseractProcessorError']
