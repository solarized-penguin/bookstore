from datetime import date, UTC, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP, ARRAY as PG_ARRAY, VARCHAR as PG_VARCHAR
from sqlmodel import SQLModel, Field


def _utc_now() -> datetime:
    return datetime.now(UTC)


class BookBase(SQLModel):
    title: str = Field(..., title="Book title", nullable=False)
    authors: list[str] = Field(
        ..., title="Book author/authors", sa_column=Column(PG_ARRAY(item_type=PG_VARCHAR, dimensions=1), nullable=False)
    )
    isbn: str = Field(..., title="Isbn", index=True, nullable=False)
    isbn13: str = Field(..., title="Isbn13", index=True, nullable=False)
    language: str = Field(..., title="Language code", nullable=False)
    pages: int = Field(..., title="Number of pages", nullable=False)
    publication_date: date = Field(
        ..., title="Publication date", sa_column=Column(PG_TIMESTAMP(timezone=False), nullable=False)
    )
    publisher: str = Field(..., title="Publisher", nullable=False)


class BookRating(SQLModel, table=True):
    __tablename__ = "book_ratings"

    book_id: int = Field(..., primary_key=True, foreign_key="books.id", title="Id of the rated book", nullable=False)
    average: float = Field(0.0, title="Average rating", nullable=False)
    votes: int = Field(0, title="Number of votes", nullable=False)
    reviews: int = Field(0, title="Number of reviews", nullable=False)


class Book(BookBase, table=True):
    __tablename__ = "books"

    id: int | None = Field(None, primary_key=True, title="Primary key")


class UserPrivileges(str, Enum):
    Client = "Client"
    Admin = "Admin"


class UserAccountStatus(str, Enum):
    Active = "Active"
    Inactive = "Inactive"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(None, primary_key=True, title="Primary Key")
    email: str = Field(..., title="Email address", unique=True, index=True, nullable=False)
    hashed_password: bytes = Field(..., title="Hashed Password", exclude=True, nullable=False)
    username: str = Field(..., title="Username", nullable=False)
    privileges: UserPrivileges = Field(UserPrivileges.Client, title="Privileges", nullable=False)
    account_status: UserAccountStatus = Field(UserAccountStatus.Active, title="Account status", nullable=False)
    created_at: datetime = Field(
        default_factory=_utc_now,
        title="Account creation date",
        sa_column=Column(PG_TIMESTAMP(timezone=True), nullable=False),
        exclude=True,
    )


class OrderStatus(str, Enum):
    Pending = "Pending"
    InDelivery = "InDelivery"
    Delivered = "Delivered"
    Cancelled = "Cancelled"


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(None, primary_key=True, title="Primary Key of the order table")
    order_date: datetime = Field(
        default_factory=_utc_now, title="Order date", sa_column=Column(PG_TIMESTAMP(timezone=True), nullable=False)
    )
    status: OrderStatus = Field(OrderStatus.Pending, title="Order status", nullable=False)
    total_price: float = Field(..., title="Total order price", nullable=False)
    user_id: int = Field(..., title="User Id", foreign_key="users.id", nullable=False)

    # books: list[Book] = Relationship(back_populates="book", sa_relationship_kwargs={"lazy": "selectin"})

    @classmethod
    def new_order(cls, user: User, books: list[Book]) -> "Order":
        # def _reserve_car(car: Car) -> Car:
        #     car.is_reserved = True
        #     return car
        #
        # reserved_cars = [_reserve_car(car) for car in cars]
        # return cls(
        #     total_price=sum(car.selling_price for car in reserved_cars),
        #     user_id=user.id,
        #     cars=reserved_cars,
        # )
        pass
