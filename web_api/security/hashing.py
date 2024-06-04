import bcrypt

from core import get_settings
from exceptions import HashingPasswordFailedException


def verify_password(password: str, db_hash_password: bytes) -> bool:
    password_bytes = password.encode(get_settings().security.user_password_encoding)
    return bcrypt.checkpw(password_bytes, db_hash_password)


def hash_password(password: str) -> bytes:
    password_bytes = password.encode(get_settings().security.user_password_encoding)
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    if bcrypt.checkpw(password_bytes, hashed_password):
        return hashed_password
    raise HashingPasswordFailedException()
