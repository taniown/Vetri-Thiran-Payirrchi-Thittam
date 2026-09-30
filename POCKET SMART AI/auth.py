from datetime import datetime
from datetime import timedelta
from datetime import timezone

from jose import JWTError
from jose import jwt

from passlib.context import CryptContext

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User


settings = get_settings()


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token"
)


def hash_password(password: str) -> str:

    return pwd_context.hash(password)


def verify_password(
    password: str,
    hashed: str
) -> bool:

    return pwd_context.verify(
        password,
        hashed
    )


def create_token(user: User) -> str:

    expiration = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": expiration
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm="HS256"
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"]
        )

        user_id = int(
            payload.get("sub")
        )

    except (
        JWTError,
        TypeError,
        ValueError
    ):

        raise credentials_exception

    user = db.get(
        User,
        user_id
    )

    if not user:
        raise credentials_exception

    return user