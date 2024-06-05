from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import Row
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession

from db import Book, BookRating, get_session
from lib import Paginator, paginate_query
from .lib import create_base_select, BookFilter
from ..base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    async def all(self, include_ratings: bool, paginator: Paginator) -> list[Book | Row[Book, BookRating]]:
        statement = paginate_query(create_base_select(include_ratings), paginator)
        return await self._db.exec(statement)

    async def by_id(self, id: int, include_ratings: bool) -> Book | Row[Book, BookRating]:
        statement = create_base_select(include_ratings).where(Book.id == id)
        return await self._db.exec(statement)

    async def by_ids(self, ids: list[int], include_ratings: bool) -> list[Book | Row[Book, BookRating]]:
        statement = create_base_select(include_ratings).where(Book.id.in_(ids))
        return await self._db.exec(statement)

    async def filter_by(
        self, include_ratings: bool, paginator: Paginator, **kwargs: Any
    ) -> list[Book | Row[Book, BookRating]]:
        statement = paginate_query(create_base_select(include_ratings), paginator)
        filters = BookFilter.create_clauses(**kwargs)
        statement = statement.where(and_(*filters)) if filters else statement
        return await self._db.exec(statement)

    @classmethod
    def create(cls, session: Annotated[AsyncSession, Depends(get_session)]) -> "BookRepository[Book]":
        return cls(session)
