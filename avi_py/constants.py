import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROJECT_ROOT=Path(__file__).parent.parent
KAKADU_BASE_PATH=os.getenv('KAKADU_HOME_PATH')
ICC_PROFILE_PATH=PROJECT_ROOT / 'color_profiles' / 'sRGB_IEC61966-2-1_no_black_scaling.icc'
EXIFTOOL_PATH='exiftool'

KAKADU_DEFAULT_OPTIONS=[
    '-num_threads', '4',
    '-double_buffering', '10',
    '-flush_period', '1024'
    '-no_weights'
]

KAKADU_DEFAULT_RECIPE=[
    'Cprecincts={256,256},{256,256},{128,128}'
    'Cblk={64,64}',
    'Cuse_sop=yes',
    'Cuse_eph=yes',
    'Corder=RPCL',
    'ORGgen_plt=yes',
    'ORGtparts=R',
    'Creversible=yes'
]
