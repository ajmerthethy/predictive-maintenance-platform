
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS
from app.db.database import get_db
from app.models.user import User

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(
        plain_password: str,
        hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        hours=JWT_EXPIRATION_HOURS
    )

    payload = {
        "sub": username,
        "exp": expires_at,
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


_bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Login via POST /auth/login to get a token.",
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: validates the bearer token and returns the
    logged-in User. Single-customer, single-tier auth - any valid token
    can access any route it's attached to, no per-user scoping.
    """

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

    except jwt.PyJWTError:
        raise unauthorized

    username = payload.get("sub")

    if not username:
        raise unauthorized

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        raise unauthorized

    return user