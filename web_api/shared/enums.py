from enum import Enum


class LogicalOperator(str, Enum):
    gt = ">"
    ge = ">="
    lt = "<"
    le = "<="
    eq = "=="


class UserPrivileges(str, Enum):
    Client = "Client"
    Admin = "Admin"


class UserAccountStatus(str, Enum):
    Active = "Active"
    Inactive = "Inactive"
