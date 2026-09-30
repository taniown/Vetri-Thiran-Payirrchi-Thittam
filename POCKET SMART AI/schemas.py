from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field


class RegisterIn(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=128
    )


class LoginIn(BaseModel):

    email: EmailStr

    password: str


class Token(BaseModel):

    access_token: str

    token_type: str = "bearer"


class HomeRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000
    )

    room_type: str = Field(
        min_length=2,
        max_length=50
    )

    style: str = Field(
        default="modern",
        max_length=50
    )

    items: dict[str, int] = Field(
        default_factory=dict
    )

    city: str = Field(
        default="Chennai",
        max_length=80
    )


class PartyRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000
    )

    guests: int = Field(
        gt=0,
        le=10_000
    )

    event_type: str = Field(
        min_length=2,
        max_length=50
    )

    venue: str = Field(
        default="Indoor",
        max_length=100
    )

    city: str = Field(
        default="Chennai",
        max_length=80
    )

    food_preference: str = Field(
        default="Mixed",
        max_length=50
    )


class JewelryRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000
    )

    occasion: str = Field(
        min_length=2,
        max_length=80
    )

    style: str = Field(
        default="elegant",
        max_length=80
    )

    outfit_color: str = Field(
        default="not specified",
        max_length=50
    )


class Recommendation(BaseModel):

    model_config = ConfigDict(
        extra="allow"
    )

    name: str
    category: str
    price: float
    platform: str
    reason: str
    url: str


class RecommendationResponse(BaseModel):

    planner: str

    budget: float

    budget_used: float

    remaining: float

    summary: str

    recommendations: list[Recommendation]

    source: str