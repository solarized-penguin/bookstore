from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.models import Order, Car, OrderStatus


async def remove_car_reservations(cars: list[Car], session: AsyncSession) -> None:
    car_ids = [car.id for car in cars]
    results = await session.execute(select(Car).filter(Car.id.in_(car_ids)))
    db_cars = results.scalars().all()
    for db_car in db_cars:
        db_car.sqlmodel_update({"is_reserved": False})
        session.add(db_car)
    await session.commit()


async def clean_up_order(order_id: int, session: AsyncSession) -> None:
    order = await session.get(Order, order_id)

    if order and order.status == OrderStatus.Cancelled:
        car_ids = [car.id for car in order.cars]
        results = await session.execute(select(Car).filter(Car.id.in_(car_ids)))
        cars = results.scalars().all()

        await remove_car_reservations(cars, session)
        await session.delete(order)

        await session.commit()
