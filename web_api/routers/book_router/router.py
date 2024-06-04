from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import ORJSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from db import Book, User
from db import get_session
from lib import Pagination
from security import UserAuthManager
from .lib import create_base_select_statement
from .models import BookRead, IncludeRatingsQuery, BookSearch

book_router = APIRouter(prefix="/book", tags=["books"], default_response_class=ORJSONResponse, include_in_schema=True)


@book_router.get("/", response_model=list[BookRead])
async def get_books(
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Depends(UserAuthManager())],
    pagination: Pagination,
    include_ratings: IncludeRatingsQuery = False,
) -> Annotated[list[BookRead], ORJSONResponse]:
    results = await session.exec(create_base_select_statement(include_ratings, pagination))
    books = [BookRead.create_book(result) for result in results]

    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No books found!")
    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content={"books": [book.model_dump(mode="json", exclude_none=True) for book in books]},
    )


@book_router.get("/{id}", response_model=BookRead)
async def get_book_by_id(
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Depends(UserAuthManager())],
    id: Annotated[int, Path(title="Book id", gt=0)],
    include_ratings: IncludeRatingsQuery = False,
) -> Annotated[BookRead, ORJSONResponse]:
    statement = create_base_select_statement(include_ratings).where(Book.id == id)
    results = await session.exec(statement)
    result = results.first()
    book = BookRead.create_book(result)

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id '{id}' not found")
    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"book": book.model_dump()})


@book_router.get("/ids/", response_model=list[BookRead])
async def get_books_by_ids(
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Depends(UserAuthManager())],
    ids: Annotated[list[int], Query(title="List of book ids", min_length=1)],
    include_ratings: IncludeRatingsQuery = False,
) -> Annotated[list[BookRead], ORJSONResponse]:
    statement = create_base_select_statement(include_ratings).where(Book.id.in_(ids))
    results = await session.exec(statement)

    books = [BookRead.create_book(result) for result in results]

    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Books not found")
    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"books": [book.model_dump() for book in books]})


@book_router.get("/search/", response_model=list[BookRead])
async def search_books(
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Depends(UserAuthManager())],
    search: BookSearch,
) -> Annotated[list[BookRead], ORJSONResponse]: ...


# @book_router.post("/filter/", response_class=ORJSONResponse, response_model=List[Car])
# async def filter_cars(
#     min_selling_price: float = Query(None, title="Minimum selling price", gt=0),
#     max_selling_price: float = Query(None, title="Maximum selling price", gt=0),
#     max_kms_driven: int = Query(None, title="Kilometers driven", gt=0),
#     no_older_than_created_in_year: int = Query(None, title="Produced not earlier than in specified year", gt=1900),
#     fewer_owners_than: int = Query(None, title="Less previous owners than", ge=0),
#     car_filter: CarFilter = Body(None),
#     session: AsyncSession = Depends(get_session),
#     _: User = Depends(UserAuthManager()),
# ) -> Annotated[List[Car], ORJSONResponse]:
#     statement = build_car_filter_statement(
#         car_filter=car_filter,
#         min_selling_price=min_selling_price,
#         max_selling_price=max_selling_price,
#         no_older_than_created_in_year=no_older_than_created_in_year,
#         max_kms_driven=max_kms_driven,
#         fewer_owners_than=fewer_owners_than,
#     )
#     results = await session.execute(statement)
#     cars = results.scalars().all()
#     if not cars:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cars meeting this criteria not found")
#     return ORJSONResponse(status_code=status.HTTP_200_OK, content={"cars": [car.model_dump() for car in cars]})
#
#
# @book_router.post("/add/", response_class=ORJSONResponse, response_model=Car)
# async def create_car(
#     new_car: CarCreate = Body(...),
#     session: AsyncSession = Depends(get_session),
#     _: User = Depends(UserAuthManager([UserPrivileges.Admin])),
# ) -> Annotated[Car, ORJSONResponse]:
#     car = Car(**new_car.dict())
#     session.add(car)
#     await session.commit()
#     await session.refresh(car)
#     return ORJSONResponse(
#         status_code=status.HTTP_201_CREATED,
#         content={"message": f"Car with id '{car.id}' created", "model": car.model_dump()},
#     )
#
#
# @book_router.delete("/remove/{car_id}", response_class=ORJSONResponse, response_model=Car)
# async def remove_car(
#     car_id: int,
#     session: AsyncSession = Depends(get_session),
#     _: User = Depends(UserAuthManager([UserPrivileges.Admin])),
# ) -> Annotated[Car, ORJSONResponse]:
#     car = await session.get(Car, car_id)
#     if not car:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Car with id '{car_id}' not found")
#
#     await session.delete(car)
#     await session.commit()
#
#     return ORJSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={"message": f"Car with id '{car.id}' removed", "model": car.model_dump()},
#     )
#
#
# @book_router.patch("/update/{car_id}", response_class=ORJSONResponse, response_model=Car)
# async def update_car(
#     car_id: int = Path(..., title="Car id", gt=0),
#     car_update: CarUpdate = Body(..., title="Update data", description="Provide only fields you want to update"),
#     session: AsyncSession = Depends(get_session),
#     _: User = Depends(UserAuthManager([UserPrivileges.Admin])),
# ) -> Annotated[Car, ORJSONResponse]:
#     car = await session.get(Car, car_id)
#     if not car:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Car with id '{car_id}' not found")
#
#     car_update_data = car_update.model_dump(exclude_none=True, exclude_unset=True)
#
#     updated_car = Car.sqlmodel_update(car, car_update_data)
#
#     session.add(updated_car)
#     await session.commit()
#     await session.refresh(updated_car)
#
#     return ORJSONResponse(
#         status_code=status.HTTP_201_CREATED, content={"message": "Model updated", "model": updated_car.model_dump()}
#     )
