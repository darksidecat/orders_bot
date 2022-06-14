from app.domain.base.exceptions.base import AppException


class RepositoryError(AppException):
    """Base repository error"""


class IntegrityViolationError(RepositoryError):
    """Violation of constraint"""
