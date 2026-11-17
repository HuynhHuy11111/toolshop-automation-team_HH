
"""
Sprint 2 - Network Interception and Mocking.

Requirements:
1. Block image requests using page.route() and route.abort().
2. Mock an empty product list using route.fulfill().
3. Verify the UI remains functional.

Run:
    pytest tests/ui/test_network.py -vv

Run with visible browser:
    pytest tests/ui/test_network.py --headed -vv
"""

import json
import re

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage


# Match product-list API on PROD and BUGGY.
# Do not match /products/search or /products/{id}.
PRODUCT_LIST = re.compile(r"/products(\?.*)?$")


# Mock response containing an empty product list.
EMPTY_PAGE = {
    "current_page": 1,
    "data": [],
    "from": None,
    "last_page": 1,
    "per_page": 9,
    "to": None,
    "total": 0,
}


# ---------------------------------------------------------
# TEST 1: BLOCK IMAGE REQUESTS
# ---------------------------------------------------------

@pytest.mark.ui
def test_network_block_images_products_still_visible(page):
    """
    Goal: Verify homepage works without product images.
    Precondition: Image requests are intercepted and aborted.
    Expected: Product names remain visible and images are blocked.
    """

    # Store blocked image URLs
    blocked_images = []

    # Match common image extensions
    image_pattern = re.compile(
        r"\.(?:png|jpe?g|webp|avif|svg)(?:\?.*)?$",
        re.IGNORECASE,
    )

    # Handler for image requests
    def block_image(route):
        blocked_images.append(route.request.url)
        route.abort()

    # Register route BEFORE opening homepage
    page.route(image_pattern, block_image)

    # Open homepage
    home = HomePage(page).open()

    # Verify product names remain visible
    expect(home.product_names.first).to_be_visible()

    # Verify products still exist
    assert home.product_names.count() > 0

    # Verify image requests were actually blocked
    assert len(blocked_images) > 0, (
        "No image requests were intercepted!"
    )


# ---------------------------------------------------------
# TEST 2: MOCK EMPTY PRODUCT LIST
# ---------------------------------------------------------

@pytest.mark.ui
def test_network_empty_product_list_shows_no_results(page):
    """
    Goal: Verify empty-state UI when API returns no products.
    Precondition: Product-list API is mocked with EMPTY_PAGE.
    Expected: Empty-state message is visible and no product cards appear.
    """

    # Intercept product-list API and return mocked JSON
    page.route(
        PRODUCT_LIST,
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(EMPTY_PAGE),
        ),
    )

    # Open homepage
    home = HomePage(page).open()

    # Verify empty-state message
    expect(home.no_results).to_be_visible()

    expect(home.no_results).to_contain_text(
        "There are no products found."
    )

    # Verify product list is empty
    expect(home.product_names).to_have_count(0)
