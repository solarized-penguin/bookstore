from datetime import date
from typing import Annotated

from fastapi import Query, Depends
from sqlmodel import SQLModel

from core import get_settings
from shared import LogicalOperator, SearchRange

search_operations = set(LogicalOperator)


def _get_average_query_params(
    average: Annotated[
        float | None, Query(title="Average ratings", description="Average ratings - between 0 and 10", ge=0, le=10)
    ] = None,
    average_operator: Annotated[
        LogicalOperator | None,
        Query(title="Operator", description="Chose operation to filter by average rating", enum=search_operations),
    ] = None,
) -> SearchRange | None:
    return SearchRange.create_range(value=average, operator=average_operator)


def _get_votes_query_params(
    votes: Annotated[int | None, Query(title="Number of votes", ge=0)] = None,
    votes_operator: Annotated[
        LogicalOperator | None,
        Query(title="Operator", description="Chose operation to filter by number of votes", enum=search_operations),
    ] = None,
) -> SearchRange | None:
    return SearchRange.create_range(value=votes, operator=votes_operator)


def _get_reviews_query_params(
    reviews: Annotated[int | None, Query(title="Number of reviews", ge=0)] = None,
    reviews_operator: Annotated[
        LogicalOperator | None,
        Query(title="Operator", description="Chose operation to filter by number of reviews", enum=search_operations),
    ] = None,
) -> SearchRange | None:
    return SearchRange.create_range(value=reviews, operator=reviews_operator)


def _get_publication_date_query_params(
    publication_date: Annotated[
        date | None, Query(title="Publication date", description="Publication date - format YYYY-MM-DD")
    ] = None,
    date_operator: Annotated[
        LogicalOperator | None,
        Query(title="Operator", description="Chose operation to filter by publication date", enum=search_operations),
    ] = None,
) -> SearchRange | None:
    return SearchRange.create_range(value=publication_date, operator=date_operator)


class RatingsSearcher(SQLModel):
    model_config = get_settings().router_models_config.config

    average: SearchRange | None = None
    votes: SearchRange | None = None
    reviews: SearchRange | None = None


class BookSearcher(SQLModel):
    model_config = get_settings().router_models_config.config

    title: str | None = None
    author: str | None = None
    publication_date: SearchRange | None = None
    publisher: str | None = None
    language: str | None = None
    ratings: RatingsSearcher | None = None


def _get_ratings_params(
    average: Annotated[SearchRange | None, Depends(_get_average_query_params)] = None,
    votes: Annotated[SearchRange | None, Depends(_get_votes_query_params)] = None,
    reviews: Annotated[SearchRange | None, Depends(_get_reviews_query_params)] = None,
) -> RatingsSearcher | None:
    return RatingsSearcher(average=average, votes=votes, reviews=reviews) if any([average, votes, reviews]) else None


RatingsQuery = Annotated[RatingsSearcher | None, Depends(_get_ratings_params)]
PublicationDateQuery = Annotated[SearchRange | None, Depends(_get_publication_date_query_params)]


def _get_book_search_params(
    ratings: RatingsQuery = None,
    publication_date: PublicationDateQuery = None,
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
