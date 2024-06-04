from starlette.middleware import Middleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware


def get_middlewares() -> list[Middleware]:
    from core import get_settings

    is_debug_on = get_settings().api.debug
    return [Middleware(ServerErrorMiddleware, debug=is_debug_on), Middleware(ExceptionMiddleware, debug=is_debug_on)]
