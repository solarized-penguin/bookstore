import re
from secrets import compare_digest
from typing import Self, Annotated, Any

from fastapi import Form
from pydantic import SecretStr, model_validator, EmailStr, model_serializer
from sqlmodel import SQLModel

from core import get_settings
from security import hash_password


class UserRegistrationForm(SQLModel):
    model_config = get_settings().router_models_config.model_config

    email: Annotated[EmailStr, Form(title="User email", description="Email, must be unique, its used for logging")]
    password: Annotated[
        SecretStr, Form(title="Password", description=get_settings().security.user_incorrect_password_message)
    ]
    repeat_password: Annotated[
        SecretStr, Form(title="Repeat password", description=get_settings().security.user_incorrect_password_message)
    ]
    username: Annotated[
        str,
        Form(
            title="Username",
            min_length=get_settings().security.username_min_length,
            max_length=get_settings().security.username_max_length,
        ),
    ]

    @property
    def hashed_password(self) -> bytes:
        return hash_password(self.password.get_secret_value())

    @model_validator(mode="after")
    def user_registration_model_validator(self) -> Self:
        password = self.password.get_secret_value()
        repeat_password = self.repeat_password.get_secret_value()

        if not compare_digest(password, repeat_password):
            raise ValueError("Passwords do not match")

        if not re.match(get_settings().security.user_password_regex, password):
            raise ValueError(get_settings().security.user_incorrect_password_message)

        return self

    @model_serializer(return_type=dict[str, Any])
    def serialize_form(self) -> dict[str, Any]:
        return {"email": self.email, "username": self.username, "hashed_password": self.hashed_password}

    @classmethod
    def create_form(
        cls,
        email: Annotated[EmailStr, Form(title="User email", description="Email, must be unique, its used for logging")],
        password: Annotated[
            SecretStr, Form(title="Password", description=get_settings().security.user_incorrect_password_message)
        ],
        repeat_password: Annotated[
            SecretStr,
            Form(title="Repeat password", description=get_settings().security.user_incorrect_password_message),
        ],
        username: Annotated[
            str,
            Form(
                title="Username",
                min_length=get_settings().security.username_min_length,
                max_length=get_settings().security.username_max_length,
            ),
        ],
    ) -> "UserRegistrationForm":
        return cls(email=email, password=password, repeat_password=repeat_password, username=username)
