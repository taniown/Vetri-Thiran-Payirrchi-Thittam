from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


Planner = Literal[
    "home",
    "party",
    "jewelry",
]


class RegisterRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=120
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class HomeItem(BaseModel):
    category: str = Field(
        min_length=2,
        max_length=80
    )

    quantity: int = Field(
        default=1,
        ge=1,
        le=50
    )


class HomeRequest(BaseModel):
    budget: int = Field(
        gt=0,
        le=10_000_000
    )

    room: str = Field(
        min_length=2,
        max_length=80
    )

    style: str = Field(
        default="modern",
        min_length=2,
        max_length=80
    )

    items: list[HomeItem] = Field(
        min_length=1,
        max_length=20
    )


class PartyRequest(BaseModel):
    budget: int = Field(
        gt=0,
        le=10_000_000
    )

    event_type: str = Field(
        min_length=2,
        max_length=80
    )

    guests: int = Field(
        gt=0,
        le=5000
    )

    venue: str = Field(
        default="home",
        min_length=2,
        max_length=100
    )

    city: str = Field(
        default="Chennai",
        min_length=2,
        max_length=100
    )

    food_preference: str = Field(
        default="mixed",
        min_length=2,
        max_length=80
    )


class Recommendation(BaseModel):
    title: str
    category: str
    platform: str

    price: int = Field(
        ge=0
    )

    quantity: int = Field(
        default=1,
        ge=1
    )

    reason: str
    url: str


class PlannerResponse(BaseModel):
    planner: Planner

    budget: int

    allocated_total: int

    remaining_budget: int

    summary: str

    recommendations: list[
        Recommendation
    ]

    source: Literal[
        "gemini",
        "fallback"
    ]

    image_insight: str | None = None


class HistoryItem(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    planner: str
    budget: int
    created_at: str