from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import Row
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from db import Book, BookRating, get_session
from lib import Paginator, paginate_query
from .lib import create_base_select, BookFilter
from .exceptions import BookWithThisIsbnAlreadyExists
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

    async def add(self, **kwargs) -> Book | tuple[Book, BookRating]:
        new_book = Book(**kwargs)
        is_book_exists = await self._verify_if_book_exists(new_book.isbn)
        if is_book_exists:
            raise BookWithThisIsbnAlreadyExists()

        self._db.add(new_book)
        await self._db.commit()
        await self._db.refresh(new_book)

        new_ratings = BookRating(**kwargs["rating"], book_id=new_book.id) if "rating" in kwargs else None

        if new_ratings:
            self._db.add(new_ratings)
            await self._db.commit()
            await self._db.refresh(new_ratings)
            return new_book, new_ratings

        return new_book

    async def _verify_if_book_exists(self, isbn: str) -> bool:
        statement = create_base_select(include_ratings=False).where(Book.isbn == isbn)
        result = await self._db.exec(statement)
        return bool(result.one_or_none())

    @classmethod
    def create(cls, session: Annotated[AsyncSession, Depends(get_session)]) -> "BookRepository[Book]":
        return cls(session)
