from app.domain.common.exceptions.base import AppException


class OrderException(AppException):
    """Base Order Exception"""


class OrderAlreadyConfirmed(OrderException):
    """Order already confirmed"""


class OrderNotExists(OrderException):
    """Order not exists"""


class OrderLineGoodsHasIncorrectType(OrderException):
    """Order line goods has incorrect type"""


class OrderAlreadyExists(OrderException):
    """Order already exists"""
