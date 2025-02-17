from typing import Any, Annotated, Collection

from sqlalchemy import Row
from sqlalchemy import func as db_func
from sqlalchemy.sql.base import ReadOnlyColumnCollection
from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import SQLModel
from sqlmodel.sql.expression import Select, SelectOfScalar, select

from db import Book, BookRating
from shared import SearchRange


def create_base_select(include_ratings: bool) -> Select[Row[Book, BookRating]] | SelectOfScalar[Book]:
    return select(Book, BookRating).join(BookRating, isouter=True) if include_ratings else select(Book)


class RatingsFilter(SQLModel):
    average: SearchRange | None = None
    votes: SearchRange | None = None
    reviews: SearchRange | None = None

    def generate_clauses(self) -> list[BinaryExpression[bool]]:
        clauses = []
        columns: ReadOnlyColumnCollection = BookRating.__table__.columns

        if self.average:
            clauses.append(self.average.create_db_clause(columns["average"]))
        if self.votes:
            clauses.append(self.average.create_db_clause(columns["votes"]))
        if self.reviews:
            clauses.append(self.average.create_db_clause(columns["reviews"]))
        return clauses


class BookFilter(SQLModel):
    title: str | None = None
    author: str | None = None
    publication_date: SearchRange | None = None
    publisher: str | None = None
    language: str | None = None
    ratings: RatingsFilter | None = None

    @classmethod
    def create_clauses(cls, **filters: Any) -> list[BinaryExpression[bool]]:
        obj = cls(**filters)

        columns: ReadOnlyColumnCollection = Book.__table__.columns

        clauses = []

        if obj.title:
            clauses.append(columns["title"].like(f"%{obj.title}%"))
        if obj.author:
            author_clause = db_func.array_to_string(columns["authors"], ",").like(f"%{obj.author}%")
            clauses.append(author_clause)
        if obj.publication_date:
            clauses.append(obj.publication_date.create_db_clause(columns["publication_date"]))
        if obj.publisher:
            clauses.append(columns["publisher"].like(f"%{obj.publisher}%"))
        if obj.language:
            clauses.append(columns["language"].like(f"%{obj.language}%"))
        if obj.ratings:
            clauses.extend(obj.ratings.generate_clauses())

        return clauses


BookWithOptionalRatings = Annotated[
    tuple[Book, BookRating | None],
    "Book with optional ratings, ratings will be returned if 'include_ratings' = true and if ratings exist",
]

BookData = (
    Collection[tuple[Book, BookRating]]
    | Collection[Row[Book, BookRating]]
    | tuple[Book, BookRating]
    | Row[Book, BookRating]
    | Book
)


def _extract_books(books: BookData, single: bool = False) -> list[BookWithOptionalRatings] | BookWithOptionalRatings:
    def _extract_one(book_data: tuple[Book, BookRating] | Row[Book, BookRating] | Book) -> BookWithOptionalRatings:
        book = book_data[0] if isinstance(book_data, Row) or isinstance(book_data, tuple) else book_data
        rating = book_data[1] if isinstance(book_data, Row) or isinstance(book_data, tuple) else None

        return book, rating

    results = [_extract_one(book) for book in books]

    if single:
        return results[0] if results else None

    return results


BookDataExtractor: Annotated[list[BookWithOptionalRatings] | BookWithOptionalRatings, _extract_books] = _extract_books
