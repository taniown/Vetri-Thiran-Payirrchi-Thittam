def register(client):

    response = client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code in (
        201,
        409,
    )

    if response.status_code == 201:
        return response.json()[
            "access_token"
        ]

    login_response = client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    return login_response.json()[
        "access_token"
    ]


def test_health(client):

    response = client.get(
        "/health"
    )

    assert response.json()[
        "status"
    ] == "ok"


def test_auth_and_home(client):

    token = register(client)

    headers = {
        "Authorization":
            f"Bearer {token}"
    }


    response = client.post(
        "/generate-home",
        headers=headers,
        json={
            "budget": 50000,

            "room": "Living Room",

            "style": "Modern",

            "items": [
                {
                    "category": "lighting",
                    "quantity": 2,
                },

                {
                    "category": "decor",
                    "quantity": 1,
                },
            ],
        },
    )


    assert response.status_code == 200

    data = response.json()

    assert data["planner"] == "home"

    assert (
        data["allocated_total"]
        <= 50000
    )


def test_party(client):

    token = register(client)

    headers = {
        "Authorization":
            f"Bearer {token}"
    }


    response = client.post(
        "/generate-party",
        headers=headers,
        json={
            "budget": 30000,

            "event_type": "Birthday",

            "guests": 30,

            "venue": "Home",

            "city": "Chennai",

            "food_preference": "Mixed",
        },
    )


    assert response.status_code == 200


def test_history_requires_auth(client):

    response = client.get(
        "/history"
    )

    assert response.status_code == 401