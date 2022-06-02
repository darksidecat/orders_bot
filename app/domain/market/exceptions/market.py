from app.domain.common.exceptions.base import AppException


class MarketException(AppException):
    """Base Market Exception"""


class MarketNotExists(MarketException):
    """Market not exist"""
