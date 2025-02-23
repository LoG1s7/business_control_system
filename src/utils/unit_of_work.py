"""The module contains base classes for supporting transactions."""

import functools
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Never

from src.database.db import async_session_maker
from src.repositories import (
    CompanyRepository,
    PositionAssignmentRepository,
    PositionInSubdivisionRepository,
    PositionRepository,
    SubdivisionRepository,
    UserRepository,
)
from src.utils.custom_types import AsyncFunc


class AbstractUnitOfWork(ABC):
    user: UserRepository

    @abstractmethod
    def __init__(self) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> Never:
        raise NotImplementedError


class UnitOfWork(AbstractUnitOfWork):
    """The class responsible for the atomicity of transactions."""

    def __init__(self) -> None:
        self.session_factory = async_session_maker
        self.is_open = False

    async def __aenter__(self) -> None:
        self.session = self.session_factory()
        self.company = CompanyRepository(self.session)
        self.user = UserRepository(self.session)
        self.subdivision = SubdivisionRepository(self.session)
        self.position = PositionRepository(self.session)
        self.position_assignment = PositionAssignmentRepository(self.session)
        self.position_in_subdivision = PositionInSubdivisionRepository(self.session)

        self.is_open = True

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if not exc_type:
            await self.commit()
        else:
            await self.rollback()
        await self.session.close()
        self.is_open = False

    async def commit(self) -> None:
        await self.session.commit()

    async def flush(self) -> None:
        await self.session.flush()

    async def rollback(self) -> None:
        await self.session.rollback()


def transaction_mode(func: AsyncFunc) -> AsyncFunc:
    """Decorate a function with transaction mode."""

    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.uow.is_open:
            res = await func(self, *args, **kwargs)
            await self.uow.flush()
            return res
        async with self.uow:
            return await func(self, *args, **kwargs)

    return wrapper
