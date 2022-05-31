from app.domain.common.exceptions.base import AppException


class GoodsException(AppException):
    """Base Goods Exception"""


class GoodsAlreadyExists(GoodsException):
    """User already exist"""


class GoodsNotExists(GoodsException):
    """User not exist"""


class CantMakeInactiveWithActiveChildren(GoodsException):
    """Can't make inactive with active children"""


class CantDeleteWithChildren(GoodsException):
    """Can't delete with children"""
