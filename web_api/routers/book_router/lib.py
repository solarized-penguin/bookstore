from sqlmodel.sql.expression import Select, SelectOfScalar, select

from db.models import Book, BookRating
from ..paginator import Paginator


def create_base_select_statement(include_ratings: bool, paginator: Paginator | None = None) -> Select | SelectOfScalar:
    base_select = select(Book, BookRating).where(Book.id == BookRating.book_id) if include_ratings else select(Book)
    if paginator:
        return (
            base_select.offset(paginator.page).limit(paginator.per_page)
            if paginator.per_page != 0
            else base_select.offset(paginator.page)
        )
    return base_select
