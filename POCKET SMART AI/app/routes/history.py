import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import current_user
from ..models.db import (
    RecommendationHistory,
    User,
)


router = APIRouter(
    tags=["history"]
)


@router.get("/history")
def history(
    limit: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    limit = min(
        max(limit, 1),
        100,
    )

    rows = db.scalars(
        select(RecommendationHistory)
        .where(
            RecommendationHistory.user_id
            == user.id
        )
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .limit(limit)
    ).all()

    return [
        {
            "id": row.id,
            "planner": row.planner,
            "budget": row.budget,
            "created_at": (
                row.created_at.isoformat()
            ),
            "request": json.loads(
                row.request_json
            ),
            "response": json.loads(
                row.response_json
            ),
        }
        for row in rows
    ]


@router.get(
    "/recommendations-details/{history_id}"
)
def details(
    history_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    row = db.scalar(
        select(RecommendationHistory)
        .where(
            RecommendationHistory.id
            == history_id,
            RecommendationHistory.user_id
            == user.id,
        )
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found",
        )

    return {
        "id": row.id,
        "planner": row.planner,
        "budget": row.budget,
        "request": json.loads(
            row.request_json
        ),
        "response": json.loads(
            row.response_json
        ),
        "created_at": (
            row.created_at.isoformat()
        ),
    }