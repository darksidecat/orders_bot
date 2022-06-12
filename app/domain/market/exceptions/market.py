from app.domain.common.exceptions.base import AppException


class MarketException(AppException):
    """Base Market Exception"""


class MarketNotExists(MarketException):
    """Market not exist"""


class CantDeleteWithOrders(MarketException):
    """Can't delete market with orders"""


class MarketAlreadyExists(MarketException):
    """Market already exists"""
