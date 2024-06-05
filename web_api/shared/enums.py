from enum import Enum


class LogicalOperator(str, Enum):
    gt = ">"
    ge = ">="
    lt = "<"
    le = "<="
    eq = "=="
