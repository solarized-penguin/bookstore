from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from fastapi.responses import ORJSONResponse

from db import User, UserPrivileges
from lib import Pagination
from repositories import BookRepository
from security import UserAuthManager
from .lib import BookSearch
from .models import BookRead, IncludeRatingsQuery, BookCreate, BookUpdate

book_router = APIRouter(prefix="/book", tags=["books"], default_response_class=ORJSONResponse, include_in_schema=True)


@book_router.get("/", response_model=list[BookRead])
async def get_books(
    repo: Annotated[BookRepository, Depends(BookRepository.create)],
    _: Annotated[User, Depends(UserAuthManager())],
    pagination: Pagination,
    include_ratings: IncludeRatingsQuery = False,
) -> Annotated[list[BookRead], ORJSONResponse]:
    results = await repo.all(include_ratings, pagination)
    books = [BookRead.create_book(result) for result in results]

    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No books found!")
    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content={"books": [book.model_dump(mode="json", exclude_none=True) for book in books]},
    )


@book_router.get("/{id}", response_model=BookRead)
async def get_book_by_id(
    repo: Annotated[BookRepository, Depends(BookRepository.create)],
    _: Annotated[User, Depends(UserAuthManager())],
    id: Annotated[int, Path(title="Book id", gt=0)],
    include_ratings: IncludeRatingsQuery = False,
) -> Annotated[BookRead, ORJSONResponse]:
    results = await repo.by_id(id, include_ratings)
    book = BookRead.create_book(results)

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id '{id}' not found")
    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"book": book.model_dump()})


@book_router.get("/ids/", response_model=list[BookRead])
async def get_books_by_ids(
    repo: Annotated[BookRepository, Depends(BookRepository.create)],
    _: Annotated[User, Depends(UserAuthManager())],
    ids: Annotated[list[int], Query(title="List of book ids", min_length=1)],
    include_ratings: IncludeRatingsQuery = False,
) -> Annotated[list[BookRead], ORJSONResponse]:
    results = await repo.by_ids(ids, include_ratings)

    books = [BookRead.create_book(result) for result in results]

    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Books not found")
    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"books": [book.model_dump() for book in books]})


@book_router.get("/search/", response_model=list[BookRead])
async def search_books(
    repo: Annotated[BookRepository, Depends(BookRepository.create)],
    _: Annotated[User, Depends(UserAuthManager())],
    search: BookSearch,
    pagination: Pagination,
    include_ratings: IncludeRatingsQuery = False,
) -> Annotated[list[BookRead], ORJSONResponse]:
    results = await repo.filter_by(
        include_ratings, pagination, **search.model_dump(exclude_none=True, exclude_unset=True)
    )

    books = [BookRead.create_book(result) for result in results]

    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Books not found")
    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"books": [book.model_dump() for book in books]})


@book_router.delete("/remove/{id}", response_class=ORJSONResponse, response_model=int)
async def remove_book(
    id: Annotated[int, Path(title="Book id", gt=0)],
    repo: Annotated[BookRepository, Depends(BookRepository.create)],
    _: Annotated[User, Depends(UserAuthManager(UserPrivileges.Admin))],
) -> Annotated[BookRead, ORJSONResponse]:
    removed_id = await repo.remove(id)

    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Book with id '{removed_id}' removed"})


@book_router.post("/add/", response_class=ORJSONResponse, response_model=BookRead)
async def create_book(
    new_book: Annotated[BookCreate, Body()],
    repo: Annotated[BookRepository, Depends(BookRepository.create)],
    _: Annotated[User, Depends(UserAuthManager(UserPrivileges.Admin))],
) -> Annotated[BookRead, ORJSONResponse]:
    result = await repo.add(**new_book.model_dump(exclude_none=True))
    book = BookRead.create_book(result)
    return ORJSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": f"Book with id '{book.id}' created", "model": book.model_dump(exclude_none=True)},
    )


@book_router.patch("/update/{id}", response_class=ORJSONResponse, response_model=BookRead)
async def update_book(
    id: Annotated[int, Path(title="Book id", gt=0)],
    update: Annotated[
        BookUpdate, Body(title="Update data", description="Partial update, unset or default values will be discarded")
    ],
    repo: Annotated[BookRepository, Depends(BookRepository.create)],
    _: Annotated[User, Depends(UserAuthManager(UserPrivileges.Admin))],
) -> Annotated[BookRead, ORJSONResponse]:
    partial_update = update.model_dump(exclude_none=True, exclude_unset=True)
    if not partial_update:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data for update supplied")

    result = await repo.update(id, **partial_update)

    book = BookRead.create_book(result)

    return ORJSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"message": f"Book with id '{book.id}' updated", "model": book.model_dump(exclude_none=True)},
    )
