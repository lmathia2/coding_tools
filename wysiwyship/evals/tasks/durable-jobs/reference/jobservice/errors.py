"""Errors safe to expose at the application boundary."""


class JobServiceError(Exception):
    pass


class ValidationError(JobServiceError, ValueError):
    pass


class JobNotFound(JobServiceError, LookupError):
    pass


class HandlerNotFound(JobServiceError, LookupError):
    pass


class LeaseLost(JobServiceError):
    """This attempt no longer has authority to mutate a running job."""


class IdempotencyConflict(JobServiceError):
    """A key was previously bound to different submission inputs."""


class JobCancelled(JobServiceError):
    """Cooperative handler interruption; not a process termination signal."""
