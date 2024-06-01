from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException, status, Path, BackgroundTasks, Form
from fastapi.responses import ORJSONResponse
from sqlmodel import select, col
from sqlmodel.ext.asyncio.session import AsyncSession

from db.models import Order, User, Car, OrderStatus, UserPrivileges
from db.session import get_session
from security.auth import UserAuthManager
from .helpers import clean_up_order
from .models import OrderInfo

order_router = APIRouter(prefix="/order", tags=["orders"])


@order_router.post("/new/", response_class=ORJSONResponse, response_model=Order)
async def create_new_order(
        car_ids: set[int] = Query(..., title="Cars to buy"),
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(UserAuthManager()),
) -> Annotated[Order, ORJSONResponse]:
    statement = select(Car).where(col(Car.id).in_(car_ids))

    cars = (await session.execute(statement)).scalars().all()
    reserved_cars = [car for car in cars if car.is_reserved]

    if any(reserved_cars):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cars with following ids are already reserved: {[car.id for car in reserved_cars]}",
        )

    new_order = Order.new_order(user=current_user, cars=cars)

    session.add(new_order)
    await session.commit()

    await session.refresh(new_order)

    return ORJSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"order": new_order.model_dump(), "reserved_cars": [car.model_dump() for car in new_order.cars]},
    )


@order_router.get("/active", response_class=ORJSONResponse, response_model=list[OrderInfo])
async def get_active_orders(
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(UserAuthManager()),
) -> Annotated[list[OrderInfo], ORJSONResponse]:
    statement = (
        select(Order)
        .where(Order.user_id == current_user.id)
        .where(col(Order.status).notin_([OrderStatus.Delivered, OrderStatus.Cancelled]))
    )

    results = await session.execute(statement)
    orders = results.scalars().all()
    return ORJSONResponse(status_code=status.HTTP_200_OK, content=[OrderInfo.create_from(order) for order in orders])


@order_router.post("/cancel/{order_id}", response_class=ORJSONResponse, response_model=Order)
async def cancel_order(
        background_tasks: BackgroundTasks,
        order_id: int = Path(..., title="Order ID", gt=0),
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(UserAuthManager()),
) -> Annotated[Order, ORJSONResponse]:
    statement = select(Order).where(Order.id == order_id).where(Order.user_id == current_user.id)

    result = await session.execute(statement)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.status != OrderStatus.Pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order is not pending, current status: {order.status}. Contact us directly to return your purchase",
        )

    order.status = OrderStatus.Cancelled

    session.add(order)
    await session.commit()
    await session.refresh(order)

    background_tasks.add_task(clean_up_order, order.id, session)

    return ORJSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"message": f"Order with id: {order.id} cancelled", "order": order.model_dump()},
    )


@order_router.patch("/update/{order_id}", response_class=ORJSONResponse, response_model=Order)
async def update_order(
        background_tasks: BackgroundTasks,
        order_id: int = Path(..., title="Order ID", gt=0),
        order_status: OrderStatus = Form(..., title="New order status"),
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(UserAuthManager(UserPrivileges.Admin)),
) -> Annotated[Order, ORJSONResponse]:
    statement = select(Order).where(Order.id == order_id)

    result = await session.execute(statement)
    order: Order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.sqlmodel_update({"status": order_status})

    session.add(order)
    await session.commit()
    await session.refresh(order)

    background_tasks.add_task(clean_up_order, order.id, session)

    return ORJSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"message": f"Order with id: {order.id} updated", "order": order.model_dump()},
    )
