from datetime import datetime, UTC
from enum import Enum
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import SQLModel, Field, Relationship


class FuelType(str, Enum):
    Diesel = "Diesel"
    Petrol = "Petrol"
    CNG = "CNG"


class SellerType(str, Enum):
    Dealer = "Dealer"
    Individual = "Individual"


class Transmission(str, Enum):
    Manual = "Manual"
    Automatic = "Automatic"


class Car(SQLModel, table=True):
    __tablename__ = "car"

    id: Optional[int] = Field(None, primary_key=True, title="Primary Key of the car table")
    car_name: str = Field(..., title="Car brand")
    year: int = Field(..., title="Year of production")
    selling_price: float = Field(..., title="Selling price")
    kms_driven: int = Field(..., title="Kilometers driven")
    fuel_type: FuelType = Field(..., title="Fuel type")
    seller_type: SellerType = Field(..., title="Seller type")
    transmission: Transmission = Field(..., title="Automatic or Manual")
    owner: int = Field(..., title="Number of previous owners")

    is_reserved: bool = Field(False, title="Is car reserved")
    order_id: Optional[int] = Field(None, foreign_key="order.id", exclude=True)
    order: Optional["Order"] = Relationship(back_populates="cars")


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
        default_factory=_utc_now,
        title="Order date",
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    status: OrderStatus = Field(OrderStatus.Pending, title="Order status")
    total_price: float = Field(..., title="Total order price")
    user_id: int = Field(..., title="User ID", foreign_key="user.id")
    cars: list[Car] = Relationship(back_populates="order", sa_relationship_kwargs={"lazy": "selectin"})

    @classmethod
    def new_order(cls, user: User, cars: list[Car]) -> "Order":
        def _reserve_car(car: Car) -> Car:
            car.is_reserved = True
            return car

        reserved_cars = [_reserve_car(car) for car in cars]
        return cls(
            total_price=sum(car.selling_price for car in reserved_cars),
            user_id=user.id,
            cars=reserved_cars,
        )
