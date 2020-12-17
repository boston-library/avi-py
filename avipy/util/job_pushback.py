import faktory
from typing import Dict
import logging
import json
from .active_job_serializer import ActiveJobWorkerSerializer

logging.basicConfig(level=logging.INFO)

def serialize_ruby_worker(**kwargs) -> Dict:
    ruby_worker = ActiveJobWorkerSerializer(**kwargs)
    return
    {
        'jid': ruby_worker.job_provider_id(),
        'args': [ruby_worker.serialize()],
        'custom': {'wrapped': ruby_worker.job_class()},
        'queue': ruby_worker.job_queue()
    }

def random_job_provider_id() -> str:
    return uuid.uuid4().hex

def job_pushback(**kwargs) -> None:
    serialized_kwargs: Dict = serialize_ruby_worker(**{**kwargs, 'job_provider_id': random_job_id()})
    logger.info('Preparing to Push job back to ruby...')
    logger.info('Arguments...')
    logger.info(json.dumps(serialized_kwargs))
    with faktory.connection() as client:
        client.queue(ActiveJobWorkerSerializer.JOB_TYPE, **serialized_kwargs)
