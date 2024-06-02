from fastapi import FastAPI
from prometheus_client import make_asgi_app

from core import get_settings
from middlewares import get_middlewares
from routers import register_routers


def create_app() -> FastAPI:
    app = FastAPI(
        title=get_settings().api.title,
        debug=get_settings().api.debug,
        version=get_settings().api.version,
        openapi_url=get_settings().api.openapi_url,
        docs_url=get_settings().api.docs_url,
        redoc_url=get_settings().api.redoc_url,
        swagger_ui_oauth2_redirect_url=get_settings().api.swagger_ui_oauth2_redirect_url,
        include_in_schema=get_settings().api.include_in_schema,
        middleware=get_middlewares(),
    )

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    register_routers(app)

    return app
