from datetime import date
from typing import Annotated

from fastapi import Query
from sqlalchemy import Row
from sqlmodel import Field

from core import get_settings
from db import BookBase, BookRatingBase as Rating, Book as BookDb, BookRating as RatingDb

IncludeRatingsQuery = Annotated[
    bool,
    Query(
        title="Should model include ratings? Defaults to False",
        description="Setting to True extends model by attaching average ratings for each book if available",
        allow_inf_nan=False,
    ),
]


class BookRead(BookBase):
    model_config = get_settings().router_models_config.config

    id: Annotated[int, Field(title="Book id", gt=0)]
    rating: Annotated[
        Rating | None,
        Field(title="Book avg rating stats", description="Average readers rating, number of votes and reviews"),
    ] = None

    @classmethod
    def create_book(cls, book_data: tuple[BookDb, RatingDb] | BookDb) -> "BookRead":
        book = book_data[0] if isinstance(book_data, tuple) else book_data
        rating = book_data[1] if isinstance(book_data, tuple) else None

        return cls(
            id=book.id,
            title=book.title,
            authors=book.authors,
            isbn=book.isbn,
            isbn13=book.isbn13,
            language=book.language,
            pages=book.pages,
            publication_date=book.publication_date,
            publisher=book.publisher,
            rating=Rating(average=rating.average, votes=rating.votes, reviews=rating.reviews) if rating else None,
        )


class BookCreate(BookBase):
    model_config = get_settings().router_models_config.config

    rating: Annotated[
        Rating | None,
        Field(title="Book avg rating stats", description="Average readers rating, number of votes and reviews"),
    ] = None


class BookUpdate(BookBase):
    model_config = get_settings().router_models_config.config

    title: Annotated[str | None, Field(title="Book title")] = None
    authors: Annotated[list[str] | None, Field(title="Book author/authors")] = None
    isbn: Annotated[str | None, Field(title="Isbn")] = None
    isbn13: Annotated[str | None, Field(title="Isbn13")] = None
    language: Annotated[str | None, Field(title="Language code")] = None
    pages: Annotated[int | None, Field(title="Number of pages", nullable=False)] = None
    publication_date: Annotated[date | None, Field(title="Publication date")] = None
    publisher: Annotated[str | None, Field(title="Publisher", nullable=False)] = None

    rating: Annotated[
        Rating | None,
        Field(title="Book avg rating stats", description="Average readers rating, number of votes and reviews"),
    ] = None
