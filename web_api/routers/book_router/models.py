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
    def create_book(cls, book_data: Row[BookDb, RatingDb] | BookDb | None) -> "BookRead | None":
        if book_data:
            book = book_data[0] if isinstance(book_data, Row) else book_data
            rating = book_data[1] if isinstance(book_data, Row) else None

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


# class CarFilter(SQLModel):
#     model_config = default_model_config
#
#     car_name: str = Field(None, title="Car brand")
#     fuel_type: FuelType = Field(None, title="Fuel type")
#     seller_type: SellerType = Field(None, title="Seller type")
#     transmission: Transmission = Field(None, title="Auto or Manual")
#
#
# def build_car_filter_statement(
#     car_filter: Optional[CarFilter],
#     min_selling_price: Optional[float],
#     max_selling_price: Optional[float],
#     no_older_than_created_in_year: Optional[int],
#     max_kms_driven: Optional[int],
#     fewer_owners_than: Optional[int],
# ) -> Statement:
#     excluded_field = "car_name"
#
#     statement = select(Car)
#
#     if car_filter:
#         filters = car_filter.model_dump(exclude_none=True)
#         statement = (
#             statement.filter_by(**filters)
#             if excluded_field not in filters
#             else statement.filter_by(**car_filter.model_dump(exclude_none=True, exclude=excluded_field))
#         )
#
#         if excluded_field in filters:
#             statement = statement.where(Car.car_name.like(f"%{car_filter.car_name}%"))
#     if min_selling_price:
#         statement = statement.where(Car.selling_price >= min_selling_price)
#     if max_selling_price:
#         statement = statement.where(Car.selling_price <= max_selling_price)
#     if no_older_than_created_in_year:
#         statement = statement.where(Car.year >= no_older_than_created_in_year)
#     if max_kms_driven:
#         statement = statement.where(Car.kms_driven <= max_kms_driven)
#     if fewer_owners_than:
#         statement = statement.where(Car.owner < fewer_owners_than)
#     return statement
