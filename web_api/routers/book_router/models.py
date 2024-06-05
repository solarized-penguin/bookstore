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

    id: int = Field(..., title="Book id", gt=0)
    rating: Rating | None = Field(
        None, title="Book avg rating stats", description="Average readers rating, number of votes and reviews"
    )

    @classmethod
    def create_book(
        cls, book_data: tuple[BookDb, RatingDb] | Row[BookDb, RatingDb] | BookDb | None
    ) -> "BookRead | None":
        if book_data:
            book = book_data[0] if isinstance(book_data, Row) or isinstance(book_data, tuple) else book_data
            rating = book_data[1] if isinstance(book_data, Row) or isinstance(book_data, tuple) else None

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
        return None


class BookCreate(BookBase):
    model_config = get_settings().router_models_config.config

    rating: Rating | None = Field(
        None, title="Book avg rating stats", description="Average readers rating, number of votes and reviews"
    )
