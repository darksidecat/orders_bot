from app.domain.common.exceptions.base import AppException


class RepositoryError(AppException):
    """Base repository error"""


class IntegrityViolationError(RepositoryError):
    """Violation of constraint"""
