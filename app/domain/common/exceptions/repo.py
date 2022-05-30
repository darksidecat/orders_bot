from app.domain.common.exceptions.base import AppException


class RepositoryError(AppException):
    """Base repository error"""


class UniqueViolationError(RepositoryError):
    """Violation of unique constraint"""
