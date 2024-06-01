from typing import Annotated, List

from fastapi import APIRouter, Depends, status, Form, HTTPException, Path
from fastapi.responses import ORJSONResponse
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, UserPrivileges
from db.session import get_session
from .models import UserRegistrationValidator
from security.auth import Token, UserAuthManager
from security.hashing import verify_password

user_router = APIRouter(prefix="/user", tags=["users"])


@user_router.post("/register/", response_model=User, response_class=ORJSONResponse)
async def register_user(
    email: str = Form(..., title="Email"),
    password: SecretStr = Form(..., title="Password"),
    repeat_password: SecretStr = Form(..., title="Repeat Password"),
    username: str = Form(..., title="Username", min_length=6),
    session: AsyncSession = Depends(get_session),
) -> Annotated[User, ORJSONResponse]:
    valid_user = UserRegistrationValidator(
        email=email, password=password, repeat_password=repeat_password, username=username
    )

    result = await session.execute(select(User).where(User.email == valid_user.email))
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    user = User(email=valid_user.email, hashed_password=valid_user.hashed_password, username=valid_user.username)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return ORJSONResponse(status_code=status.HTTP_201_CREATED, content={"user": user.model_dump()})


@user_router.post("/login/", response_class=ORJSONResponse)
async def login_user(
    email: Annotated[str, Form(..., title="Email", alias="username")],
    password: Annotated[SecretStr, Form(..., title="Password", alias="password")],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ORJSONResponse:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or password are incorrect")
    elif not verify_password(password.get_secret_value(), user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    return ORJSONResponse(Token.create_access_token(user))


@user_router.get("/", response_model=List[User], response_class=ORJSONResponse)
async def get_users(
    session: Annotated[AsyncSession, Depends(get_session)],
    _: User = Depends(UserAuthManager([UserPrivileges.Admin])),
) -> Annotated[List[User], ORJSONResponse]:
    results = await session.execute(select(User))
    users = results.scalars().all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content={"users": [user.model_dump() for user in users]},
    )


@user_router.get("/{id}/", response_model=User, response_class=ORJSONResponse)
async def get_user(
    id: int = Path(..., title="User id", gt=0),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(UserAuthManager([UserPrivileges.Admin])),
) -> Annotated[User, ORJSONResponse]:
    user = await session.get(User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id '{id}' not found")
    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"user": user.model_dump()})


@user_router.get("/current", response_model=User, response_class=ORJSONResponse)
async def get_logged_user(user: Annotated[User, Depends(UserAuthManager())]) -> Annotated[User, ORJSONResponse]:
    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"user": user.model_dump()})
