
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

KAKADU_BASE_PATH=os.getenv('KAKADU_HOME_PATH')
CONSOLE_DEBUG_MODE=(os.getenv('AVI_DEBUG', 'false').lower() == 'true')
# NOTE: May not need the source folder path below. But definetley in the avi processor
PROJECT_ROOT=Path(__file__).parent.parent
ICC_PROFILE_PATH=PROJECT_ROOT / 'color_profiles' / 'sRGB_IEC61966-2-1_no_black_scaling.icc'
EXIFTOOL_PATH=os.getenv('EXIFTOOL_PATH', 'exiftool')
COLOR_MODES=['RGB', 'RGBA']
VALID_IMAGE_EXTENSIONS=['.tiff', '.tif']

KDU_DEFAULT_LAYER_COUNT=8
KDU_DEFAULT_TILE_SIZE=1024
IMAGE_DEFAULT_COMPRESSION=10
IMAGE_MAX_LEVEL_SIZE=96

KAKADU_DEFAULT_OPTIONS=[
    '-num_threads', '4',
    '-double_buffering', '10',
    '-flush_period', '1024',
    '-no_weights'
]
if not CONSOLE_DEBUG_MODE:
    KAKADU_DEFAULT_OPTIONS += ['-quiet']

KAKADU_DEFAULT_RECIPE=[
    'Cblk={64,64}',
    'Cuse_sop=yes',
    'Cuse_eph=yes',
    'Corder=RPCL',
    'ORGgen_plt=yes',
    'ORGtparts=R',
]
