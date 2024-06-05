from datetime import datetime, date
from enum import Enum
from typing import Annotated

from fastapi import Query, Depends
from sqlmodel import SQLModel

from core import get_settings


class SearchingOperator(str, Enum):
    gt = ">"
    ge = ">="
    lt = "<"
    le = "<="
    eq = "=="


search_operations = set(SearchingOperator)


class SearchRange(SQLModel):
    model_config = get_settings().router_models_config.config

    value: float | int | date | datetime | None
    operator: SearchingOperator | None


def _get_average_query_params(
    average: Annotated[
        float | None, Query(title="Average ratings", description="Average ratings - between 0 and 10", ge=0, le=10)
    ] = None,
    average_operator: Annotated[
        SearchingOperator | None,
        Query(title="Operator", description="Chose operation to filter by average rating", enum=search_operations),
    ] = None,
) -> SearchRange:
    return SearchRange(value=average, operator=average_operator)


def _get_votes_query_params(
    votes: Annotated[int | None, Query(title="Number of votes", ge=0)] = None,
    votes_operator: Annotated[
        SearchingOperator | None,
        Query(title="Operator", description="Chose operation to filter by number of votes", enum=search_operations),
    ] = None,
) -> SearchRange:
    return SearchRange(value=votes, operator=votes_operator)


def _get_reviews_query_params(
    reviews: Annotated[int | None, Query(title="Number of reviews", ge=0)] = None,
    reviews_operator: Annotated[
        SearchingOperator | None,
        Query(title="Operator", description="Chose operation to filter by number of reviews", enum=search_operations),
    ] = None,
) -> SearchRange:
    return SearchRange(value=reviews, operator=reviews_operator)


def _get_publication_date_query_params(
    publication_date: Annotated[
        date | None, Query(title="Publication date", description="Publication date - format YYYY-MM-DD")
    ] = None,
    date_operator: Annotated[
        SearchingOperator | None,
        Query(title="Operator", description="Chose operation to filter by publication date", enum=search_operations),
    ] = None,
) -> SearchRange:
    return SearchRange(value=publication_date, operator=date_operator)


class RatingsSearcher(SQLModel):
    model_config = get_settings().router_models_config.config

    average: SearchRange | None
    votes: SearchRange | None
    reviews: SearchRange | None


class BookSearcher(SQLModel):
    model_config = get_settings().router_models_config.config

    title: str | None
    author: str | None
    publication_date: SearchRange | None
    publisher: str | None
    language: str | None
    ratings: RatingsSearcher | None


def _get_ratings_params(
    average: Annotated[SearchRange | None, Depends(_get_average_query_params)] = None,
    votes: Annotated[SearchRange | None, Depends(_get_votes_query_params)] = None,
    reviews: Annotated[SearchRange | None, Depends(_get_reviews_query_params)] = None,
) -> RatingsSearcher:
    return RatingsSearcher(average=average, votes=votes, reviews=reviews)


RatingsQuery = Annotated[RatingsSearcher, Depends(_get_ratings_params)]
PublicationDateQuery = Annotated[SearchRange, Depends(_get_publication_date_query_params)]


def _get_book_search_params(
    ratings: RatingsQuery,
    publication_date: PublicationDateQuery,
    title: Annotated[str | None, Query(title="Book title", description="Find books with title like...")] = None,
    author: Annotated[
        str | None, Query(title="Author name", description="Find books with author with name like...")
    ] = None,
    publisher: Annotated[
        str | None, Query(title="Publisher name", description="Find books with publisher named like...")
    ] = None,
    language: Annotated[
        str | None, Query(title="Language like", description="Find books with language like...")
    ] = None,
) -> BookSearcher:
    return BookSearcher(
        title=title,
        author=author,
        publication_date=publication_date,
        publisher=publisher,
        language=language,
        ratings=ratings,
    )


BookSearch = Annotated[BookSearcher, Depends(_get_book_search_params)]
