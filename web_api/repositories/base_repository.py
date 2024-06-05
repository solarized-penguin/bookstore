from typing import Annotated, Protocol, TypeVar, runtime_checkable

from fastapi import Depends
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from abc import abstractmethod

from db import get_session


T = TypeVar("T", bound=SQLModel)


@runtime_checkable
class BaseRepository(Protocol[T]):
    _db: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._db = session

    @classmethod
    @abstractmethod
    def create(cls, session: Annotated[AsyncSession, Depends(get_session)]) -> "BaseRepository[T]": ...
