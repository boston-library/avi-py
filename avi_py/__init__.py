"""avi_py."""
__version__ = "0.2"
__author__ = "Benjamin Barber (bbarber@bpl.org)"
#pylint: disable=wrong-import-position
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

from .entry_points import convert_jp2_main, ffmpeg_thumbnail_main

__all__ = ['convert_jp2_main', 'ffmpeg_thumbnail_main']
#pylint: enable=wrong-import-position
