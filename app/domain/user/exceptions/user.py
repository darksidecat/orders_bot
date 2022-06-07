from app.domain.common.exceptions.base import AppException


class UserException(AppException):
    """Base User Exception"""


class UserAlreadyExists(UserException):
    """User already exist"""


class UserNotExists(UserException):
    """User not exist"""


class UserWithNoAccessLevels(UserException):
    """User must have at least one access level"""


class BlockedUserWithOtherRole(UserException):
    """Blocked user can have only that role"""


class CantDeleteWithOrders(UserException):
    """Can't delete user with orders"""
