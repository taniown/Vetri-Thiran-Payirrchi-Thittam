from datetime import (
    datetime,
    timedelta,
    timezone,
)

import hashlib
import hmac
import secrets

import jwt

from ..config import get_settings


ALGORITHM = "HS256"


def hash_password(
    password: str,
) -> str:

    salt = secrets.token_bytes(16)

    digest = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
    )

    return (
        f"scrypt$"
        f"{salt.hex()}$"
        f"{digest.hex()}"
    )


def verify_password(
    password: str,
    encoded: str,
) -> bool:

    try:

        _,
        salt_hex,
        digest_hex = encoded.split(
            "$",
            2,
        )

        salt = bytes.fromhex(
            salt_hex
        )

        actual = hashlib.scrypt(
            password.encode(),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
        )

        return hmac.compare_digest(
            actual.hex(),
            digest_hex,
        )

    except (
        ValueError,
        TypeError,
    ):
        return False


def create_access_token(
    user_id: int,
) -> str:

    settings = get_settings()

    now = datetime.now(
        timezone.utc
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": (
            now
            + timedelta(
                minutes=(
                    settings.access_token_expire_minutes
                )
            )
        ),
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> int:

    settings = get_settings()

    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[ALGORITHM],
    )

    return int(
        payload["sub"]
    )