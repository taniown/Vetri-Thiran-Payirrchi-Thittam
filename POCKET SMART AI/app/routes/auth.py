from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import current_user
from ..models.db import User
from ..models.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from ..services.security import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    # Check whether the email already exists
    existing_user = db.scalar(
        select(User).where(
            User.email == payload.email.lower()
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Create new user
    user = User(
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create JWT token
    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    # Find user
    user = db.scalar(
        select(User).where(
            User.email == payload.email.lower()
        )
    )

    # Validate credentials
    if (
        not user
        or not verify_password(
            payload.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Return access token
    return TokenResponse(
        access_token=create_access_token(user.id)
    )


@router.post("/logout")
def logout(
    _: User = Depends(current_user),
):
    return {
        "message": (
            "Logout acknowledged. "
            "Delete the bearer token on the client."
        )
    }


@router.get("/session-info")
def session_info(
    user: User = Depends(current_user),
):
    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }


@router.get("/session-data")
def session_data(
    user: User = Depends(current_user),
):
    return {
        "user_id": user.id,
        "name": user.name,
        "login_status": "active",
    }


@router.post(
    "/token",
    response_model=TokenResponse,
)
def token(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    return login(payload, db)