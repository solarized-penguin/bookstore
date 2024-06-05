from typing import Any

from sqlmodel import SQLModel, Field

# from db.models import Car, Order


#
#
# class OrderInfo(SQLModel):
#     model_config = default_model_config
#
#     order: Order = Field(..., title="Order")
#     cars: list[Car] = Field(..., title="Cars in the order")
#
#     @classmethod
#     def create_from(cls, order: Order) -> dict[str, Any]:
#         return cls(order=order, cars=list(order.cars)).model_dump()
