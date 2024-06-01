import re
from secrets import compare_digest
from typing import Self

from email_validator import validate_email
from pydantic import SecretStr, model_validator
from sqlmodel import SQLModel, Field

from core import get_settings
from security.hashing import hash_password
from ..default_model_config import default_model_config

settings = get_settings()
settings_security = settings.security


class UserRegistrationValidator(SQLModel):
    model_config = default_model_config

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
        if not len(self.username) >= settings_security.username_min_length:
            raise ValueError("Username is too short")
        if not len(self.username) <= settings_security.username_max_length:
            raise ValueError("Username is too long")

    @model_validator(mode="after")
    def user_registration_model_validator(self) -> Self:
        self._email_validator()
        self._username_validator()

        password = self.password.get_secret_value()
        repeat_password = self.repeat_password.get_secret_value()

        if not compare_digest(password, repeat_password):
            raise ValueError("Passwords do not match")

        if not re.match(settings_security.user_password_regex, password):
            raise ValueError(settings_security.user_incorrect_password_message)

        return self
