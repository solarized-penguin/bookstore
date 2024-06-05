from datetime import date, datetime

from sqlalchemy import Column
from sqlmodel import SQLModel

from core import get_settings
from .enums import LogicalOperator


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
