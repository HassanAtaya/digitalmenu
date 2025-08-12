from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from ..core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str, role: str, restaurant_id: str | None = None, restaurant_slug: str | None = None, expires_delta: int | None = None) -> str:
    if expires_delta is None:
        expires_delta = settings.access_token_expire_minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    to_encode: dict[str, object] = {"exp": expire, "sub": subject, "role": role}
    if restaurant_id:
        to_encode["restaurant_id"] = restaurant_id
    if restaurant_slug:
        to_encode["restaurant_slug"] = restaurant_slug
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


