from typing import Annotated, Any

from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db import User, get_session
from .exceptions import UserWithThisEmailAlreadyExists
from ..base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    async def all(self) -> list[User]:
        results = await self._db.exec(select(User))
        return results.all()

    async def by_id(self, id: int) -> User | None:
        result = await self._db.exec(select(User).where(User.id == id))
        return result.one_or_none()

    async def by_email(self, email: str) -> User | None:
        result = await self._db.exec(select(User).where(User.email == email))
        return result.one_or_none()

    async def add(self, **kwargs: Any) -> User:
        new_user = User(**kwargs)
        db_user = await self.by_email(new_user.email)

        if db_user:
            raise UserWithThisEmailAlreadyExists()

        self._db.add(new_user)
        await self._db.commit()
        await self._db.refresh(new_user)

        return new_user

    @classmethod
    def create(cls, session: Annotated[AsyncSession, Depends(get_session)]) -> "UserRepository[User]":
        return cls(session)
