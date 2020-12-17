import typing
import logging
from pathlib import Path
from faktory import Worker
from avi_py.processors import JP2Processor

def job_runner(img_path: Path):
    pass

def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    w = Worker(queues=['python'], concurrency=1)
    w.register('PyJp2Worker', job_runner)
    w.run()

if __name__ == '__main__':
    main()
