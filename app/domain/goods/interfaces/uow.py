from app.domain.base.interfaces.uow import IUoW
from app.domain.goods.interfaces.persistence import IGoodsReader, IGoodsRepo


class IGoodsUoW(IUoW):
    goods: IGoodsRepo
    goods_reader: IGoodsReader
