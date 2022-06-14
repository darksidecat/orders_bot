from app.domain.base.exceptions.base import AppException


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


class CantSetFolderSKU(GoodsException):
    """Can't set folder SKU"""


class CantMakeActiveWithInactiveParent(GoodsException):
    """Can't make active with inactive parent"""


class GoodsTypeCantBeParent(GoodsException):
    """Goods with GoodsType.Goods can't be parent"""


class CantSetSKUForFolder(GoodsException):
    """Can't set SKU for folder"""


class GoodsMustHaveSKU(GoodsException):
    """Goods must have SKU"""
