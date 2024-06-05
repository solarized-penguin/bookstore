from datetime import date, datetime
from typing import Annotated

from pydantic import Field, EmailStr
from sqlalchemy import Column
from sqlmodel import SQLModel
from core import get_settings
from .enums import LogicalOperator, UserPrivileges, UserAccountStatus
from .lib import utc_now


class SearchRange(SQLModel):
    model_config = get_settings().router_models_config.config

    value: float | int | date | datetime
    operator: LogicalOperator

    def create_db_clause(self, c: Column):
        match self.operator:
            case LogicalOperator.gt:
                return c > self.value
            case LogicalOperator.ge:
                return c >= self.value
            case LogicalOperator.lt:
                return c < self.value
            case LogicalOperator.le:
                return c <= self.value
            case LogicalOperator.eq:
                return c == self.value

    @classmethod
    def create_range(
        cls, value: float | int | date | datetime | None, operator: LogicalOperator | None
    ) -> "SearchRange | None":
        return cls(value=value, operator=operator) if value and operator else None


class UserRead(SQLModel):
    email: Annotated[EmailStr, Field(title="Email address")]
    username: Annotated[str, Field(title="Username")]
    account_status: Annotated[UserAccountStatus, Field(title="Account status")] = UserAccountStatus.Active
    privileges: Annotated[UserPrivileges, Field(title="Privileges")] = UserPrivileges.Client
    created_at: Annotated[datetime, Field(default_factory=utc_now, title="Account creation date")]

    @classmethod
    def create_user(cls, user_data: SQLModel) -> "UserRead":
        return cls(**user_data.model_dump())
