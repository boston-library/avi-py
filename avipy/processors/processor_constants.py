import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path('../../../') / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

KAKADU_BASE_PATH=os.getenv('KAKADU_HOME_PATH')
