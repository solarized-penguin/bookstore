from fastapi import FastAPI


def register_routers(app: FastAPI) -> None:
    from .user_router import user_router
    from .book_router import book_router

    app.include_router(user_router)
    app.include_router(book_router)
