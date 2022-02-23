import sys
import logging

from argparse import ArgumentParser, Namespace
from pathlib import Path
from . import constants as avi_const
from .avi_jp2_processor import AviJp2Processor
from .avi_ffmpeg_processor import AviFFMpegProcessor

__LOG_FORMAT = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
__DEFAULT_LOG_PATH = str(Path.cwd() / 'logs' / 'avi_convert_jp2.log')
__JP2_PARSER_DESC = "Generate a JP2 from a TIFF. Adds sRGB_IEC61966-2-1_no_black_scaling icc profile if is color. Prevalidates image before conversion"
__FFMPEG_THUMB_PARSER_DESC = "Generate a 300x300 pixel thumbnail from a given .mov or .mp4 file"

__all__ = ['convert_jp2_main', 'ffmpeg_thumbnail_main']

def convert_jp2_main() -> None:
    """
    A basic command line script that runs :func:`~avi_py.avi_jp2_processor.AviJp2Processor.process_jp2`"
    """

    args = __parse_jp2_args()
    __setup_logger(args.log_file, args.log_level)

    try:
        jp2_conversion = AviJp2Processor.process_jp2(args.src_file_path, args.dest_file_path)
        json_result = jp2_conversion.json_result()
        if jp2_conversion.success:
            print("{}".format(json_result), end='')
        else:
            sys.exit("Error! {}".format(json_result))
    except FileNotFoundError as f_ex:
        sys.exit("Error! {}".format(str(f_ex)))


def ffmpeg_thumbnail_main() -> None:
    """
    A basic command line script that runs :func:`~avi_py.avi_ffmpeg_processor.AviFFMpegProcessor.process_thumbnail`"
    """

    args = __parse_ffmpeg_thumbnail_args()
    __setup_logger(args.log_file, args.log_level)

    try:
        ffmpeg_thumb = AviFFMpegProcessor.process_thumbnail(args.src_file_path, args.dest_file_path)
        json_result = ffmpeg_thumb.json_result()
        if ffmpeg_thumb.success:
            print("{}".format(json_result), end='')
        else:
            sys.exit("Error! {}".format(json_result))
    except FileNotFoundError as f_ex:
        sys.exit("Error! {}".format(str(f_ex)))

def __setup_logger(log_file: str, log_level: str='debug') -> None:
    """
    Sets up the logger. Writes to console as well a file if AVI_DEBUG=true
    """

    root_logger = logging.getLogger(__name__)
    root_logger.setLevel(log_level)

    file_handler = logging.FileHandler(log_file, mode='a+')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(__LOG_FORMAT)
    root_logger.add_handler(file_handler)
    if avi_const.CONSOLE_DEBUG_MODE:
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(__LOG_FORMAT)
        root_logger.addHandler(stream_handler)

def __parse_ffmpeg_thumbnail_args(parser: ArgumentParser=ArgumentParser(prog='avi_ffmpeg_thumbnail',
                                            description=__FFMPEG_THUMB_PARSER_DESC)) -> Namespace:
    parser.add_argument('src_file_path', type=str, help='Full path to the source mov|mp4 file to covert')
    parser.add_argument('dest_file_path', type=str, help='Path to jpg thumbnail output file')
    parser.add_argument('-Lf', '--log_file', type=str, help='Path to a log file to output', required=False, default=__DEFAULT_LOG_PATH)
    parser.add_argument('-Ll', '--log_level', type=str, help='Log level[debug|info|warning|error|critical]', required=False, default='debug')
    return parser.parse_args()

def __parse_jp2_args(parser: ArgumentParser=ArgumentParser(prog='avi_jp2_convert',
                                            description=__JP2_PARSER_DESC)) -> Namespace:
    parser.add_argument('src_file_path', type=str, help='Full path to the source mov or mp4 file to covert')
    parser.add_argument('dest_file_path', type=str, help='Path to jp2 output file')
    parser.add_argument('-Lf', '--log_file', type=str, help='Path to a log file to output', required=False, default=__DEFAULT_LOG_PATH)
    parser.add_argument('-Ll', '--log_level', type=str, help='Log level[debug|info|warning|error|critical]', required=False, default='debug')
    return parser.parse_args()
