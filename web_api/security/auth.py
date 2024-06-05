from datetime import datetime, UTC
from functools import cached_property
from typing import Any, Annotated, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import computed_field
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, Field, select

from core import get_settings
from db import User, UserPrivileges
from db import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login/")


def _token_creation_timestamp_utc() -> int:
    return int(datetime.now(UTC).timestamp())


class TokenPayload(SQLModel):
    sub: str = Field(..., title="User email")
    iat: int = Field(default_factory=_token_creation_timestamp_utc, title="Token issue date")
    name: str = Field(..., title="User name")

    @computed_field(title="Token expiration date", return_type=int, repr=True)
    @cached_property
    def exp(self) -> int:
        iat_datetime = datetime.fromtimestamp(self.iat, UTC)
        expiration_time = iat_datetime + get_settings().security.jwt_token_default_expire_timedelta
        return int(expiration_time.timestamp())

    @classmethod
    def create_payload_from_db_user(cls, db_user: User) -> dict[str, Any]:
        return cls(sub=db_user.email, name=db_user.username).model_dump()


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

    @classmethod
    def create_access_token(cls, db_user: User) -> dict[str, str]:
        access_token = jwt.encode(
            TokenPayload.create_payload_from_db_user(db_user),
            key=get_settings().security.jwt_secret_key,
            algorithm=get_settings().security.jwt_algorithm,
        )
        return cls(access_token=access_token).model_dump()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
    required_privileges: List[UserPrivileges],
) -> User:
    payload = jwt.decode(
        token, get_settings().security.jwt_secret_key, algorithms=[get_settings().security.jwt_algorithm]
    )

    email = payload.get("sub")
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if required_privileges and user.privileges not in required_privileges:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return user


class UserAuthManager:
    def __init__(self, required_privileges: list[UserPrivileges] | UserPrivileges | None = None) -> None:
        if required_privileges:
            self.required_privileges = (
                required_privileges if isinstance(required_privileges, list) else [required_privileges]
            )
        else:
            self.required_privileges = list(UserPrivileges)

    async def __call__(
        self, token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[AsyncSession, Depends(get_session)]
    ) -> User:
        return await get_current_user(token, session, self.required_privileges)
