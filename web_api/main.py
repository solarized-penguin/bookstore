from fastapi import FastAPI
from prometheus_client import make_asgi_app

from core import get_settings, get_logger
from middlewares.exceptions.exception import ExceptionHandlerMiddleware
from routers.book_router import book
from routers.order_router import order
from routers.user_router import user


def create_app() -> FastAPI:
    logger = get_logger(__name__)

    logger.info(f"{get_settings().api.title} is starting...")

    app = FastAPI(
        title=get_settings().api.title,
        debug=get_settings().api.debug,
        version=get_settings().api.version,
        openapi_url=get_settings().api.openapi_url,
        docs_url=get_settings().api.docs_url,
        redoc_url=get_settings().api.redoc_url,
        swagger_ui_oauth2_redirect_url=get_settings().api.swagger_ui_oauth2_redirect_url,
        include_in_schema=get_settings().api.include_in_schema,
    )

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    app.include_router(car.car_router)
    app.include_router(user.user_router)
    app.include_router(order.order_router)

    app.add_middleware(ExceptionHandlerMiddleware)

    return app
