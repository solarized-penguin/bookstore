from typing import Annotated

from fastapi import Depends
from sqlalchemy import Row
from sqlmodel.ext.asyncio.session import AsyncSession

from lib import Paginator, paginate_query
from ..base_repository import BaseRepository
from db import Book, BookRating, get_session
from sqlmodel.sql.expression import Select, SelectOfScalar, select


def _create_base_select(include_ratings: bool) -> Select[tuple[Book, BookRating]] | SelectOfScalar[Book]:
    return select(Book, BookRating).where(Book.id == BookRating.book_id) if include_ratings else select(Book)


class BookRepository(BaseRepository[Book]):
    async def all(
        self, include_ratings: bool, paginator: Annotated[Paginator, None] = None
    ) -> list[Book | Row[Book, BookRating]]:
        statement = paginate_query(_create_base_select(include_ratings), paginator)
        return await self._db.exec(statement)

    async def by_id(self, id: int, include_ratings: bool) -> Book | Row[Book, BookRating]:
        statement = _create_base_select(include_ratings).where(Book.id == id)
        return await self._db.exec(statement)

    async def by_ids(self, ids: list[int], include_ratings: bool) -> list[Book | Row[Book, BookRating]]:
        statement = _create_base_select(include_ratings).where(Book.id.in_(ids))
        return await self._db.exec(statement)

    @classmethod
    def create(cls, session: Annotated[AsyncSession, Depends(get_session)]) -> "BookRepository[Book]":
        return cls(session)
