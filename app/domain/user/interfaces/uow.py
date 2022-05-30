from app.domain.common.interfaces.uow import IUoW
from app.domain.user.interfaces.persistence import IUserReader, IUserRepo


class IUserUoW(IUoW):
    user: IUserRepo
    user_reader: IUserReader
