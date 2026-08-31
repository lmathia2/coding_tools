"""Errors safe to expose at the application boundary."""


class JobServiceError(Exception):
    pass


class ValidationError(JobServiceError, ValueError):
    pass


class JobNotFound(JobServiceError, LookupError):
    pass


class HandlerNotFound(JobServiceError, LookupError):
    pass
