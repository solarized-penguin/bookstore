import uvicorn
import logging

from sqlalchemy import Dialect
from sqlmodel import and_, select

from repositories.book_repository.lib import RatingsFilter, Book, BookFilter, BookRating
from shared import LogicalOperator
from web_api.core import get_settings

if __name__ == "__main__":
    print("Running with settings: ", get_settings().model_dump_json(indent=2))

    config = uvicorn.Config(
        "web_api:create_app", factory=True, host="0.0.0.0", port=8080, reload=True, log_level=logging.DEBUG
    )
    server = uvicorn.Server(config)
    server.run()

    # bk = Book.__table__.columns
    # bk_r = BookRating.__table__.columns
    # r = RatingsFilter(
    #     **{
    #         "average": {"value": 3.42, "operator": LogicalOperator.ge},
    #         "votes": {"value": 17, "operator": LogicalOperator.gt},
    #         "reviews": {"value": 17, "operator": LogicalOperator.ge},
    #     }
    # )
    # d = {
    #     "title": "HP",
    #     "author": "J",
    #     "publication_date": {"value": "2014-01-01", "operator": LogicalOperator.ge},
    #     "publisher": "B",
    #     "language": "en",
    #     "ratings": r.model_dump(),
    # }
    #
    # f = BookFilter.create_clauses(**d)
    #
    # f = and_(*f)
    #
    # q = select(Book, BookRating).where(Book.id == BookRating.book_id).where(f)
    #
    # print(q.compile().compile_state)
