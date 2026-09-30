import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..dependencies import current_user
from ..models.db import (
    RecommendationHistory,
    User,
)
from ..models.schemas import (
    HomeRequest,
    PartyRequest,
)
from ..services.gemini import build_plan


router = APIRouter(
    tags=["planners"]
)


settings = get_settings()


async def _image(
    file: UploadFile | None,
):
    if not file:
        return None, None

    allowed = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if file.content_type not in allowed:
        raise HTTPException(
            status_code=415,
            detail=(
                "Only JPEG, PNG, or WebP "
                "images are supported"
            ),
        )

    data = await file.read()

    if (
        len(data)
        > settings.max_upload_mb * 1024 * 1024
    ):
        raise HTTPException(
            status_code=413,
            detail=(
                f"Image exceeds "
                f"{settings.max_upload_mb} MB"
            ),
        )

    return data, file.content_type


def _save(
    db: Session,
    user: User,
    planner: str,
    budget: int,
    request_data: dict,
    result: dict,
):
    history = RecommendationHistory(
        user_id=user.id,
        planner=planner,
        budget=budget,
        request_json=json.dumps(
            request_data
        ),
        response_json=json.dumps(
            result
        ),
    )

    db.add(history)
    db.commit()


def _response(
    planner: str,
    budget: int,
    result: dict,
):
    total = sum(
        item["price"] * item["quantity"]
        for item in result["recommendations"]
    )

    return {
        "planner": planner,
        "budget": budget,
        "allocated_total": total,
        "remaining_budget": max(
            0,
            budget - total
        ),
        **result,
    }


@router.post("/generate-home")
def generate_home(
    payload: HomeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    data = payload.model_dump()

    result = build_plan(
        "home",
        payload.budget,
        data,
    )

    _save(
        db,
        user,
        "home",
        payload.budget,
        data,
        result,
    )

    return _response(
        "home",
        payload.budget,
        result,
    )


@router.post("/generate-party")
def generate_party(
    payload: PartyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    data = payload.model_dump()

    result = build_plan(
        "party",
        payload.budget,
        data,
    )

    _save(
        db,
        user,
        "party",
        payload.budget,
        data,
        result,
    )

    return _response(
        "party",
        payload.budget,
        result,
    )


@router.post("/generate-jewelry")
async def generate_jewelry(
    budget: int = Form(
        ...,
        gt=0,
        le=10_000_000,
    ),
    occasion: str = Form(
        ...,
        min_length=2,
        max_length=80,
    ),
    style: str = Form(
        "minimal",
        min_length=2,
        max_length=80,
    ),
    outfit_notes: str = Form(
        "",
        max_length=500,
    ),
    outfit_image: UploadFile | None = File(
        None
    ),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    image_bytes, mime = await _image(
        outfit_image
    )

    data = {
        "budget": budget,
        "occasion": occasion,
        "style": style,
        "outfit_notes": outfit_notes,
    }

    result = build_plan(
        "jewelry",
        budget,
        data,
        image_bytes,
        mime,
    )

    _save(
        db,
        user,
        "jewelry",
        budget,
        data,
        result,
    )

    return _response(
        "jewelry",
        budget,
        result,
    )