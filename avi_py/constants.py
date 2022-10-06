import os
from pathlib import Path

KAKADU_BASE_PATH=os.getenv('KAKADU_HOME', '')
CONSOLE_DEBUG_MODE=(str(os.getenv('AVI_DEBUG', 'false')).lower() == 'true')
# NOTE: May not need the source folder path below. But definetley in the avi processor
PROJECT_ROOT=Path(__file__).parent.parent
ICC_PROFILE_PATH=PROJECT_ROOT / 'color_profiles' / 'sRGB_IEC61966-2-1_no_black_scaling.icc'
EXIFTOOL_PATH=os.getenv('EXIFTOOL_PATH', 'exiftool')
COLOR_MODES=['RGB', 'RGBA']
VALID_IMAGE_EXTENSIONS=['.tiff', '.tif']
VALID_VIDEO_EXTENSIONS=['.mov', '.mp4', '.avi']
VALID_AUDIO_EXTENSIONS=['.wav']
MAX_CONCURRENCY=min(32, os.cpu_count() + 4)
KDU_DEFAULT_LAYER_COUNT=8
KDU_DEFAULT_TILE_SIZE=1024
IMAGE_DEFAULT_COMPRESSION=10
IMAGE_MAX_LEVEL_SIZE=96

# Get screenshot five seconds into video
FFMPEG_DEFAULT_SS_TIME=5
FFMPEG_THUMBNAIL_SIZE=(300, 300)

FFMPEG_AUDIO_ARGS={'ar': '44100', 'ac': 2, 'audio_bitrate': '192k', 'acodec': 'libmp3lame', 'f': 'mp3'}

KAKADU_DEFAULT_OPTIONS=[
    '-num_threads', str(os.cpu_count()),
    '-double_buffering', '10',
    '-flush_period', '1024',
    '-no_weights'
]
if CONSOLE_DEBUG_MODE:
    MAGICK_DEFAULT_CONVERT_COMMANDS=[
        'convert',
        '-compress',
        'none'
    ]
else:
    MAGICK_DEFAULT_CONVERT_COMMANDS=[
        'convert',
        '-quiet',
        '-compress',
        'none'
    ]
    KAKADU_DEFAULT_OPTIONS += ['-quiet']

KAKADU_DEFAULT_RECIPE=[
    'Cblk={64,64}',
    'Cuse_sop=yes',
    'Cuse_eph=yes',
    'Corder=RPCL',
    'ORGgen_plt=yes',
    'ORGtparts=R',
]

TESS_DEFAULT_LANG=r'osd+eng'
TESS_DEFAULT_CFG=r'--oem 1 --psm 1 --dpi 300'
TESS_OUT_FILE_TYPES={'pdf': 'pdf', 'alto': 'xml'}
