from datetime import date, UTC, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import SQLModel, Field, Relationship


class BookRating(SQLModel, table=True):
    __tablename__ = "rating"

    book_id: int = Field(..., primary_key=True, foreign_key="book.id", title="Id of the rated book")
    average: float = Field(0, title="Average rating")
    votes: int = Field(0, title="Number of votes")
    reviews: int = Field(0, title="Number of reviews")


class Book(SQLModel, table=True):
    __tablename__ = "book"

    id: int | None = Field(None, primary_key=True, title="Primary key")
    title: str = Field(..., title="Book title")
    author: str = Field(..., title="Book author/authors")
    isbn: str = Field(..., title="Isbn")
    isbn13: str = Field(..., title="Isbn13")
    language: str = Field(..., title="Language code")
    pages: int = Field(..., title="Number of pages")
    publication_date: date = Field(..., title="Publication date")
    publisher: str = Field(..., title="Publisher")


class UserPrivileges(str, Enum):
    Client = "Client"
    Admin = "Admin"


class UserAccountStatus(str, Enum):
    Active = "Active"
    Inactive = "Inactive"


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(None, primary_key=True, title="Primary Key of the user table")
    email: str = Field(..., title="Email address", unique=True, index=True)
    hashed_password: bytes = Field(..., title="Hashed Password", exclude=True)
    username: str = Field(..., title="Username")
    privileges: UserPrivileges = Field(UserPrivileges.Client, title="Privileges")
    account_status: UserAccountStatus = Field(UserAccountStatus.Active, title="Account status")


class OrderStatus(str, Enum):
    Pending = "Pending"
    InDelivery = "InDelivery"
    Delivered = "Delivered"
    Cancelled = "Cancelled"


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Order(SQLModel, table=True):
    __tablename__ = "order"

    id: Optional[int] = Field(None, primary_key=True, title="Primary Key of the order table")
    order_date: datetime = Field(
        default_factory=_utc_now, title="Order date", sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )
    status: OrderStatus = Field(OrderStatus.Pending, title="Order status")
    total_price: float = Field(..., title="Total order price")
    user_id: int = Field(..., title="User ID", foreign_key="user.id")
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
