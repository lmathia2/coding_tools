"""Stable domain errors shared by direct service calls and the HTTP-like adapter."""


class DomainError(Exception):
    def __init__(self, status, code, message):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message

    def payload(self):
        return {"error": {"code": self.code, "message": self.message}}


def missing():
    return DomainError(404, "not_found", "Resource not found")


def forbidden():
    return DomainError(403, "forbidden", "Operation not permitted")


def invalid(message):
    return DomainError(400, "invalid_request", message)
