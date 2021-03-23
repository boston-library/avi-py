import argparse
import sys
import logging

from avi_py.avi_jp2_image import AviJp2Image

def avi_convert_jp2():
    """
    A basic command line script that runs :func:`~avi_py.avi_jp2_image.AviJp2Image.convert_to_jp2`"
    """

    parser = argparse.ArgumentParser(description="Generate a JP2 from a TIFF. Adds sRGB_IEC61966-2-1_no_black_scaling icc profile if is color. Prevalidates image before conversion")
    parser.add_argument('src_file_path', help='Full path to the source tiff file to covert')
    parser.add_argument('-Lf', '--log_file', help='Path to a log file to output', required=False, default=None)
    parser.add_argument('-Ll', '--log_level', help='Log level[debug|info|warning|error|critical]', required=False, default='debug')
    args = parser.parse_args()

    log_file = args.log_file
    log_level = logging.getLevelName(args.log_level.upper())
    if not log_file:
        logging.basicConfig(stream=sys.stdout, level=log_level)
    else:
        logging.basicConfig(filename=log_file, level=log_level)

    avi_jp2_convert = AviJp2Image(args.src_file_path)
    avi_jp2_convert.convert_to_jp2()

    if avi_jp2_convert.result.get('success') is False:
        sys.exit(avi_jp2_convert.json_result())

    print(avi_jp2_convert.json_result(), file=sys.stdout)
