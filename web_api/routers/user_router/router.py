from typing import Annotated, List

from fastapi import APIRouter, Depends, status, Form, HTTPException, Path
from fastapi.responses import ORJSONResponse
from pydantic import SecretStr

from shared import UserPrivileges
from repositories import UserRepository
from security import Token, UserAuthManager, verify_password, UserRead
from .lib import UserRegistrationForm

user_router = APIRouter(prefix="/user", tags=["users"], default_response_class=ORJSONResponse, include_in_schema=True)


@user_router.post("/register/", response_model=UserRead)
async def register_user(
    user_form: Annotated[UserRegistrationForm, Depends(UserRegistrationForm.create_form)],
    repo: Annotated[UserRepository, Depends(UserRepository.create)],
) -> Annotated[UserRead, ORJSONResponse]:
    new_user = await repo.add(**user_form.model_dump())
    user = UserRead.create_user(new_user)
    return ORJSONResponse(status_code=status.HTTP_201_CREATED, content={"user": user.model_dump()})


@user_router.post("/login/")
async def login_user(
    email: Annotated[str, Form(..., title="Email", alias="username")],
    password: Annotated[SecretStr, Form(..., title="Password", alias="password")],
    repo: Annotated[UserRepository, Depends(UserRepository.create)],
) -> ORJSONResponse:
    db_user = await repo.by_email(email)

    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or password are incorrect")
    elif not verify_password(password.get_secret_value(), db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    return ORJSONResponse(Token.create_access_token(UserRead.create_user(db_user)))


@user_router.get("/", response_model=List[UserRead])
async def get_users(
    repo: Annotated[UserRepository, Depends(UserRepository.create)],
    _: UserRead = Depends(UserAuthManager(UserPrivileges.Admin)),
) -> Annotated[List[UserRead], ORJSONResponse]:
    db_users = await repo.all()

    if not db_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")

    users = [UserRead.create_user(db_user) for db_user in db_users]

    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"users": [user.model_dump() for user in users]})


@user_router.get("/{id}", response_model=UserRead)
async def get_user(
    id: Annotated[int, Path(title="User id", gt=0)],
    repo: Annotated[UserRepository, Depends(UserRepository.create)],
    _: UserRead = Depends(UserAuthManager(UserPrivileges.Admin)),
) -> Annotated[UserRead, ORJSONResponse]:
    db_user = await repo.by_id(id)

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id '{id}' not found")

    user = UserRead.create_user(db_user)

    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"user": user.model_dump()})


@user_router.get("/current/", response_model=UserRead)
async def get_logged_user(user: Annotated[UserRead, Depends(UserAuthManager())]) -> Annotated[UserRead, ORJSONResponse]:
    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"user": user.model_dump()})


# @user_router.get("/remove/{id}", response_model=int)
