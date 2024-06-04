from typing import Annotated

from fastapi import Query, Depends
from sqlmodel import SQLModel

PageQuery = Annotated[int, Query(title="Skip x records", ge=0)]
PerPageQuery = Annotated[
    int,
    Query(
        title="How many records per page?", description="Setting this to 0 fetches everything since chosen page.", ge=0
    ),
]


class Paginator(SQLModel):
    page: int
    per_page: int


def _get_pagination_params(page: PageQuery = 0, per_page: PerPageQuery = 20) -> Paginator:
    return Paginator(page=page, per_page=per_page)


Pagination = Annotated[Paginator, Depends(_get_pagination_params)]
