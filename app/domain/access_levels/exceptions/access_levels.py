from app.domain.common.exceptions.base import AppException


class AccessLevelException(AppException):
    """Base Exception for AccessLevel"""


class AccessLevelNotExist(AccessLevelException):
    """Access level with this id not found"""
