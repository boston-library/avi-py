from typing import List, Union, Any
import uuid
from datetime import datetime, time

ArgList = List[Union[int, str]]

class ActiveJobWorkerSerializer:
    JOB_TYPE = 'ActiveJob::QueueAdapters::FaktoryAdapter::JobWrapper'
    def __init__(self, **kwargs: Any) -> None:
        self.__ruby_job_class: str = kwargs['job_class']
        self.__ruby_job_arguments: ArgList = kwargs['job_arguments']
        self.__ruby_job_provider_id: str = kwargs['job_provider_id']
        self.__ruby_job_id: str = str(uuid.uuid4())
        self.__ruby_queue_name: str = kwargs['queue']

    @property
    def job_id(self) -> str:
        return self.__job_id

    @property
    def job_provider_id(self) -> str:
        return self.__ruby_job_provider_id

    @property
    def job_arguments(self) -> List[Union[int, str]]:
        return self.__ruby_job_arguments

    @property
    def job_class(self) -> str:
        return self.__ruby_job_class

    @property
    def job_queue(self) -> str:
        return self.__ruby_queue_name

    @property
    def priority(self) -> str:
        # Add constant lookup here
        pass

    @property
    def executions(self) -> int:
        return 0

    @property
    def exception_executions(self) -> Dict:
        return {}

    @property
    def timezone(self) -> str:
        str(datetime.now().astimezone().tzinfo)

    @property
    def enqueued_at(self) -> str:
        return datetime.utcnow().isoformat()

    def serialize(self) -> Dict:
        return {
            "job_class": self.job_class,
            "job_id": self.job_id,
            "provider_job_id": self.provider_job_id,
            "queue_name": self.queue_name,
            "priority": self.priority,
            "arguments": self.arguments,
            "executions": self.executions,
            "exception_executions": self.exception_executions,
            "locale": self.locale,
            "timezone": self.timezone,
            "enqueued_at": self.enqueued_at.
        }
