from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from jose import JWTError, JOSEError, ExpiredSignatureError
from jose.exceptions import JWTClaimsError
from starlette.middleware.base import BaseHTTPMiddleware

from core import get_logger
from exceptions.custom_exceptions import LoginFailedPasswordDoesNotMatchException, HashingPasswordFailedException

logger = get_logger(__name__)


def handle_jwt_errors(exception: JOSEError) -> ORJSONResponse:
    logger.exception(exception)

    if issubclass(exception.__class__, ExpiredSignatureError):
        return ORJSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"error": "Token has expired"})
    elif issubclass(exception.__class__, JWTError):
        return ORJSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"error": "Unauthorized"})
    elif issubclass(exception.__class__, JWTClaimsError):
        return ORJSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"error": "Token claims are invalid"})


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except JWTError as jwt_error:
            return handle_jwt_errors(jwt_error)
        except ValueError as value_error:
            errors = value_error.errors()
            logger.exception({"error": e["msg"] for e in errors})
            return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": e["msg"] for e in errors})
        except HashingPasswordFailedException as hashing_error:
            logger.error(hashing_error)
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal Server Error", "message": "An unexpected error occurred."},
            )
        except LoginFailedPasswordDoesNotMatchException as password_does_not_match:
            logger.exception(password_does_not_match)
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Provided password does not match provided email"},
            )
        except HTTPException as http_exception:
            logger.exception(http_exception)
            return ORJSONResponse(status_code=http_exception.status_code, content=http_exception.detail)
        except RequestValidationError as request_validation_error:
            logger.error(request_validation_error.errors())
            return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=request_validation_error.errors())
        except Exception as exception:
            logger.exception(exception)
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal Server Error", "message": "An unexpected error occurred."},
            )
