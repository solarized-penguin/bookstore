from typing import TypeVar, Optional

from sqlmodel import SQLModel, Field, select

from db.models import FuelType, SellerType, Transmission, Car
from ..default_model_config import default_model_config

Statement = TypeVar("Statement")


class CarCreate(SQLModel):
    model_config = default_model_config

    car_name: str = Field(..., title="Car brand")
    year: int = Field(..., title="Production year")
    selling_price: float = Field(..., title="Selling price")
    kms_driven: int = Field(..., title="Kilometers driven")
    fuel_type: FuelType = Field(..., title="Fuel type")
    seller_type: SellerType = Field(..., title="Seller type")
    transmission: Transmission = Field(..., title="Auto or Manual")
    owner: int = Field(..., title="Number of previous owners")


class CarUpdate(SQLModel):
    model_config = default_model_config

    car_name: str = Field(None, title="Car brand")
    year: int = Field(None, title="Production year")
    selling_price: float = Field(None, title="Selling price")
    kms_driven: int = Field(None, title="Kilometers driven")
    fuel_type: FuelType = Field(None, title="Fuel type")
    seller_type: SellerType = Field(None, title="Seller type")
    transmission: Transmission = Field(None, title="Auto or Manual")
    owner: int = Field(None, title="Number of previous owners")


class CarFilter(SQLModel):
    model_config = default_model_config

    car_name: str = Field(None, title="Car brand")
    fuel_type: FuelType = Field(None, title="Fuel type")
    seller_type: SellerType = Field(None, title="Seller type")
    transmission: Transmission = Field(None, title="Auto or Manual")


def build_car_filter_statement(
    car_filter: Optional[CarFilter],
    min_selling_price: Optional[float],
    max_selling_price: Optional[float],
    no_older_than_created_in_year: Optional[int],
    max_kms_driven: Optional[int],
    fewer_owners_than: Optional[int],
) -> Statement:
    excluded_field = "car_name"

    statement = select(Car)

    if car_filter:
        filters = car_filter.model_dump(exclude_none=True)
        statement = (
            statement.filter_by(**filters)
            if excluded_field not in filters
            else statement.filter_by(**car_filter.model_dump(exclude_none=True, exclude=excluded_field))
        )

        if excluded_field in filters:
            statement = statement.where(Car.car_name.like(f"%{car_filter.car_name}%"))
    if min_selling_price:
        statement = statement.where(Car.selling_price >= min_selling_price)
    if max_selling_price:
        statement = statement.where(Car.selling_price <= max_selling_price)
    if no_older_than_created_in_year:
        statement = statement.where(Car.year >= no_older_than_created_in_year)
    if max_kms_driven:
        statement = statement.where(Car.kms_driven <= max_kms_driven)
    if fewer_owners_than:
        statement = statement.where(Car.owner < fewer_owners_than)
    return statement
