from app.domain.base.interfaces.uow import IUoW
from app.domain.order.interfaces.persistence import IOrderReader, IOrderRepo


class IOrderUoW(IUoW):
    order: IOrderRepo
    order_reader: IOrderReader
