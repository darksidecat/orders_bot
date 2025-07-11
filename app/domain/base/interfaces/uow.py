from typing import Protocol


class IUoW(Protocol):
    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...
