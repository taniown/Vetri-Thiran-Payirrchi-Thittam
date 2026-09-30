import json
from typing import Any

from ..config import get_settings
from .catalog import fallback_recommendations


class GeminiService:

    def __init__(self):

        settings = get_settings()

        self.model = settings.gemini_model
        self.client = None

        if settings.gemini_api_key:

            try:
                from google import genai

                self.client = genai.Client(
                    api_key=settings.gemini_api_key
                )

            except ImportError:
                self.client = None

    def available(self) -> bool:
        return self.client is not None

    def _prompt(
        self,
        planner: str,
        budget: int,
        data: dict,
        image_note: str | None = None,
    ) -> str:

        return f"""
You are PocketSmart AI,
a budget planning assistant.

Create practical recommendations.

Planner:
{planner}

Budget INR:
{budget}

User data:
{json.dumps(data, ensure_ascii=False)}

Image insight:
{image_note or 'none'}

Return ONLY valid JSON with these keys:

summary
recommendations
image_insight

Each recommendation must contain:

title
category
platform
price
quantity
reason
url

Platforms must be selected only from:

Amazon
Flipkart
IKEA
Swiggy
Zomato
OYO

Use plausible indicative INR prices.

Never claim live availability.

Keep the total recommendation cost
within the user's budget.

For URLs use search/result URLs rather
than pretending to know an exact
product page.
"""

    def generate(
        self,
        planner: str,
        budget: int,
        data: dict,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
    ) -> dict[str, Any] | None:

        if not self.client:
            return None

        from google.genai import types

        parts: list[Any] = [
            self._prompt(
                planner,
                budget,
                data,
            )
        ]

        if image_bytes and mime_type:

            parts.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                )
            )

        try:

            response = (
                self.client.models.generate_content(
                    model=self.model,
                    contents=parts,
                    config=(
                        types.GenerateContentConfig(
                            temperature=0.35,
                            response_mime_type=(
                                "application/json"
                            ),
                        )
                    ),
                )
            )

            raw = response.text or ""

            return json.loads(raw)

        except Exception:
            return None


def build_plan(
    planner: str,
    budget: int,
    data: dict,
    image_bytes: bytes | None = None,
    mime_type: str | None = None,
) -> dict:

    service = GeminiService()

    ai = service.generate(
        planner,
        budget,
        data,
        image_bytes,
        mime_type,
    )

    if (
        ai
        and isinstance(
            ai.get("recommendations"),
            list,
        )
    ):

        recommendations = []

        for item in ai["recommendations"]:

            try:

                recommendations.append(
                    {
                        "title": str(
                            item["title"]
                        ),

                        "category": str(
                            item["category"]
                        ),

                        "platform": str(
                            item["platform"]
                        ),

                        "price": max(
                            0,
                            int(item["price"]),
                        ),

                        "quantity": max(
                            1,
                            int(
                                item.get(
                                    "quantity",
                                    1,
                                )
                            ),
                        ),

                        "reason": str(
                            item.get(
                                "reason",
                                "Budget-aware suggestion.",
                            )
                        ),

                        "url": str(
                            item.get(
                                "url",
                                "",
                            )
                        ),
                    }
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

        if recommendations:

            total = sum(
                item["price"]
                * item["quantity"]
                for item in recommendations
            )

            if total <= budget:

                return {
                    "summary": str(
                        ai.get(
                            "summary",
                            "Your personalized plan is ready.",
                        )
                    ),

                    "recommendations": (
                        recommendations
                    ),

                    "image_insight": ai.get(
                        "image_insight"
                    ),

                    "source": "gemini",
                }

    recommendations = fallback_recommendations(
        planner,
        budget,
        data,
    )

    return {
        "summary": (
            "A local budget-aware plan "
            "was generated because live "
            "AI recommendations were "
            "unavailable or did not pass "
            "validation."
        ),

        "recommendations": recommendations,

        "image_insight": (
            "Image received; add a Gemini "
            "API key to enable visual analysis."
            if image_bytes
            else None
        ),

        "source": "fallback",
    }