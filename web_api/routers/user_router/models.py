import re
from secrets import compare_digest
from typing import Self

from email_validator import validate_email
from pydantic import SecretStr, model_validator
from sqlmodel import SQLModel, Field

from core import get_settings
from security import hash_password


class UserRegistrationValidator(SQLModel):
    model_config = get_settings().router_models_config.model_config

    email: str = Field(...)
    password: SecretStr = Field(...)
    repeat_password: SecretStr
    username: str = Field(...)

    @property
    def hashed_password(self) -> bytes:
        return hash_password(self.password.get_secret_value())

    def _email_validator(self) -> None:
        try:
            validate_email(self.email)
        except Exception as ex:
            raise ValueError("This is not a valid email address")

    def _username_validator(self) -> None:
        if not len(self.username) >= get_settings().security.username_min_length:
            raise ValueError("Username is too short")
        if not len(self.username) <= get_settings().security.username_max_length:
            raise ValueError("Username is too long")

    @model_validator(mode="after")
    def user_registration_model_validator(self) -> Self:
        self._email_validator()
        self._username_validator()

        password = self.password.get_secret_value()
        repeat_password = self.repeat_password.get_secret_value()

        if not compare_digest(password, repeat_password):
            raise ValueError("Passwords do not match")

        if not re.match(get_settings().security.user_password_regex, password):
            raise ValueError(get_settings().security.user_incorrect_password_message)

        return self
