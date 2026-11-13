
"""
Sprint 2 - API Testing and Parametrize.

Requirements:
- At least 5 API tests.
- At least 2 HTTP methods.
- Test HTTP 4xx.
- Validate JSON structure.
- Test Bearer Token.
- Two parametrized test functions.
- One parametrized test reads data from JSON.

Run:
    pytest tests/api/test_api_sprint2.py -vv
"""

import json
from pathlib import Path

import pytest

from conftest import new_email, register_user, strong_password


pytestmark = pytest.mark.api


# ---------------------------------------------------------
# LOAD TEST DATA FROM JSON
# ---------------------------------------------------------

DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "search_cases.json"
)

SEARCH_CASES = json.loads(
    DATA_FILE.read_text(encoding="utf-8")
)


# ---------------------------------------------------------
# TEST 1: GET API STATUS
# ---------------------------------------------------------

def test_api_status_returns_200(api):

    response = api.get("/status")

    assert response.status == 200, response.text()

    body = response.json()

    assert body["app_name"] == "Toolshop"


# ---------------------------------------------------------
# TEST 2: GET PRODUCTS - JSON STRUCTURE
# ---------------------------------------------------------

def test_api_products_returns_valid_json_structure(api):

    response = api.get("/products")

    assert response.status == 200, response.text()

    body = response.json()

    required_keys = {
        "current_page",
        "data",
        "per_page",
        "total",
        "last_page"
    }

    assert required_keys.issubset(body.keys())

    products = body["data"]

    assert isinstance(products, list)
    assert len(products) > 0

    per_page = body["per_page"]

    assert isinstance(per_page, int)
    assert per_page > 0
    assert len(products) <= per_page

    for product in products:

        assert product.get("id") is not None

        assert isinstance(product.get("name"), str)
        assert product["name"].strip() != ""

        assert isinstance(product.get("price"), (int, float))
        assert product["price"] > 0


# ---------------------------------------------------------
# TEST 3: POST REGISTER - PASSWORD SECURITY
# ---------------------------------------------------------

def test_api_register_does_not_expose_password(api):

    email = new_email()
    password = strong_password()

    response = register_user(api, email, password)

    assert response.status == 201, response.text()

    body = response.json()

    assert "password" not in body


# ---------------------------------------------------------
# TEST 4: PARAMETRIZE - HTTP 401 AND 404
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "endpoint, expected_status",
    [
        pytest.param(
            "/users/me",
            401,
            id="unauthorized-user"
        ),
        pytest.param(
            "/products/does-not-exist",
            404,
            id="missing-product"
        ),
    ]
)
def test_api_error_responses(api, endpoint, expected_status):

    response = api.get(endpoint)

    assert response.status == expected_status, response.text()


# ---------------------------------------------------------
# TEST 5: BEARER TOKEN AUTHENTICATION
# ---------------------------------------------------------

def test_api_authenticated_user_can_access_profile(
    api,
    auth_headers,
    test_user
):

    response = api.get(
        "/users/me",
        headers=auth_headers
    )

    assert response.status == 200, response.text()

    body = response.json()

    assert body["email"] == test_user["email"]


# ---------------------------------------------------------
# TEST 6: PARAMETRIZE - READ SEARCH DATA FROM JSON
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "case",
    SEARCH_CASES,
    ids=[case["keyword"] for case in SEARCH_CASES]
)
def test_api_search_returns_matching_products(api, case):

    response = api.get(
        "/products/search",
        params={"q": case["keyword"]}
    )

    assert response.status == 200, response.text()

    body = response.json()

    # Support both list and paginated JSON responses.
    if isinstance(body, dict):
        products = body.get("data", body.get("products"))
    else:
        products = body

    assert isinstance(products, list), (
        f"Unexpected response structure: {body}"
    )

    assert len(products) > 0, (
        f"No products found for: {case['keyword']}"
    )

    for product in products:

        name = product.get("name", "")

        assert isinstance(name, str)

        assert case["must_contain"].casefold() in name.casefold(), (
            f"Product '{name}' does not contain "
            f"'{case['must_contain']}'"
        )
