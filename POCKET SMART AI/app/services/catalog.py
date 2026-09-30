from urllib.parse import quote_plus


def search_url(
    platform: str,
    query: str,
) -> str:

    q = quote_plus(query)

    bases = {
        "Amazon": (
            f"https://www.amazon.in/s?k={q}"
        ),

        "Flipkart": (
            f"https://www.flipkart.com/search?q={q}"
        ),

        "IKEA": (
            "https://www.ikea.com/in/en/"
            f"search/?q={q}"
        ),

        "Swiggy": (
            f"https://www.swiggy.com/search?query={q}"
        ),

        "Zomato": (
            f"https://www.zomato.com/search?q={q}"
        ),

        "OYO": (
            "https://www.oyorooms.com/"
            f"search?location={q}"
        ),
    }

    return bases.get(
        platform,
        f"https://www.google.com/search?q={q}",
    )


CATALOG = [
    (
        "home",
        "lighting",
        "LED ceiling light",
        "Amazon",
        1499,
    ),

    (
        "home",
        "lighting",
        "Warm floor lamp",
        "IKEA",
        3999,
    ),

    (
        "home",
        "furniture",
        "Compact study table",
        "Amazon",
        5499,
    ),

    (
        "home",
        "furniture",
        "Two-seater sofa",
        "IKEA",
        12999,
    ),

    (
        "home",
        "decor",
        "Minimal wall art set",
        "Flipkart",
        1299,
    ),

    (
        "home",
        "decor",
        "Indoor planter",
        "IKEA",
        999,
    ),

    (
        "party",
        "food",
        "Party catering package",
        "Zomato",
        450,
    ),

    (
        "party",
        "food",
        "Snack and beverage package",
        "Swiggy",
        300,
    ),

    (
        "party",
        "decoration",
        "Birthday decoration kit",
        "Amazon",
        999,
    ),

    (
        "party",
        "decoration",
        "Elegant event decor kit",
        "Flipkart",
        1799,
    ),

    (
        "party",
        "venue",
        "Budget hotel/event stay",
        "OYO",
        2499,
    ),

    (
        "jewelry",
        "earrings",
        "Pearl drop earrings",
        "Amazon",
        899,
    ),

    (
        "jewelry",
        "necklace",
        "Minimal pendant necklace",
        "Flipkart",
        1299,
    ),

    (
        "jewelry",
        "bracelet",
        "Classic charm bracelet",
        "Amazon",
        1099,
    ),

    (
        "jewelry",
        "earrings",
        "Oxidized statement earrings",
        "Flipkart",
        699,
    ),
]


def fallback_recommendations(
    planner: str,
    budget: int,
    data: dict,
) -> list[dict]:

    rows = [
        row
        for row in CATALOG
        if row[0] == planner
    ]

    if planner == "home":

        requested = {
            item["category"].lower()
            for item in data.get(
                "items",
                []
            )
        }

        rows = [
            row
            for row in rows
            if row[1] in requested
        ] or rows

        target = min(
            8,
            max(
                3,
                len(
                    data.get(
                        "items",
                        []
                    )
                ) * 2,
            ),
        )

    elif planner == "party":
        target = 6

    else:
        target = 6

    rows = sorted(
        rows,
        key=lambda row: row[4]
    )

    result = []
    total = 0

    for (
        domain,
        category,
        title,
        platform,
        price,
    ) in rows * 3:

        quantity = 1

        if (
            planner == "party"
            and category == "food"
        ):
            quantity = max(
                1,
                min(
                    20,
                    (
                        data.get(
                            "guests",
                            10
                        )
                        + 9
                    ) // 10,
                ),
            )

        cost = price * quantity

        if total + cost <= budget:

            result.append(
                {
                    "title": title,
                    "category": category,
                    "platform": platform,
                    "price": price,
                    "quantity": quantity,
                    "reason": (
                        "Fits the "
                        f"{data.get('style', data.get('event_type', data.get('occasion', 'your')))} "
                        "preference while keeping "
                        "the plan budget-aware."
                    ),
                    "url": search_url(
                        platform,
                        title,
                    ),
                }
            )

            total += cost

        if len(result) >= target:
            break

    return result