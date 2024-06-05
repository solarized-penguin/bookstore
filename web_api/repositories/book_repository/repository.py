from typing import Annotated, Any

from fastapi import Depends
from sqlmodel import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from shared import Paginator, paginate_query
from db import Book, BookRating, get_session
from .exceptions import BookWithThisIsbnAlreadyExists
from .lib import create_base_select, BookFilter, BookWithOptionalRatings, BookDataExtractor
from ..base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    async def all(self, include_ratings: bool, paginator: Paginator) -> list[BookWithOptionalRatings]:
        statement = paginate_query(create_base_select(include_ratings), paginator)
        results = await self._db.exec(statement)
        return BookDataExtractor(results)

    async def by_id(self, id: int, include_ratings: bool) -> BookWithOptionalRatings | None:
        statement = create_base_select(include_ratings).where(Book.id == id)
        results = await self._db.exec(statement)
        return BookDataExtractor(results, single=True)

    async def by_ids(self, ids: list[int], include_ratings: bool) -> list[BookWithOptionalRatings]:
        statement = create_base_select(include_ratings).where(Book.id.in_(ids))
        results = await self._db.exec(statement)
        return BookDataExtractor(results)

    async def filter_by(
        self, include_ratings: bool, paginator: Paginator, **kwargs: Any
    ) -> list[BookWithOptionalRatings]:
        statement = paginate_query(create_base_select(include_ratings), paginator)
        filters = BookFilter.create_clauses(**kwargs)
        statement = statement.where(and_(*filters)) if filters else statement
        results = await self._db.exec(statement)
        return BookDataExtractor(results)

    async def add(self, **kwargs: Any) -> BookWithOptionalRatings:
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

    async def remove(self, id: int) -> int:
        book, ratings = await self.by_id(id, include_ratings=True)

        if ratings:
            await self._db.delete(ratings)
            await self._db.commit()

        await self._db.delete(book)
        await self._db.commit()

        return book.id

    async def update(self, id: int, **kwargs: Any) -> BookWithOptionalRatings:
        book, ratings = await self.by_id(id, include_ratings=True)

        updated_book = Book.sqlmodel_update(book, {k: v for k, v in kwargs.items() if k != "rating"})
        updated_ratings = (
            BookRating.sqlmodel_update(ratings, kwargs["rating"]) if ratings and "rating" in kwargs else None
        )

        self._db.add(updated_book)
        await self._db.commit()
        await self._db.refresh(updated_book)

        if updated_ratings:
            self._db.add(updated_ratings)
            await self._db.commit()
            await self._db.refresh(updated_ratings)

        return updated_book, updated_ratings

    async def _verify_if_book_exists(self, isbn: str) -> bool:
        statement = create_base_select(include_ratings=False).where(Book.isbn == isbn)
        result = await self._db.exec(statement)
        return bool(result.one_or_none())

    @classmethod
    def create(cls, session: Annotated[AsyncSession, Depends(get_session)]) -> "BookRepository[Book]":
        return cls(session)
