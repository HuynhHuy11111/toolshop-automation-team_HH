
"""
Sprint 2B - BDD Shopping Cart.

BDD step definitions reuse existing Page Objects.
No new locators are created in this file.

Run:
    pytest tests/bdd -v
"""

import pytest

from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from pages.home_page import HomePage


# ==========================================================
# PYTEST MARKERS
# ==========================================================

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.ui,
]


# ==========================================================
# LOAD FEATURE
# ==========================================================

scenarios("cart.feature")


# ==========================================================
# GIVEN - OPEN HOME PAGE
# ==========================================================

@given(
    "I am on the home page",
    target_fixture="home"
)
def open_home_page(page):

    home = HomePage(page).open()

    expect(home.product_names.first).to_be_visible()

    return home


# ==========================================================
# WHEN - OPEN PRODUCT
# ==========================================================

@when(
    parsers.parse('I open the product "{product}"'),
    target_fixture="product_page"
)
def open_product(home, product):

    return home.open_product(product)


# ==========================================================
# WHEN - ADD PRODUCT TO CART
# ==========================================================

@when(
    parsers.parse(
        "I add it to the cart with quantity {quantity:d}"
    ),
    target_fixture="cart_context"
)
def add_product_to_cart(product_page, quantity):

    # Read unit price before adding the product
    unit_price = product_page.price()

    # Add product with selected quantity
    product_page.add_to_cart(quantity)

    # Wait for successful notification
    expect(product_page.toast).to_contain_text(
        "Product added to shopping cart"
    )

    # Verify cart badge
    expect(product_page.cart_quantity).to_have_text(
        str(quantity)
    )

    # Navigate to shopping cart
    cart = product_page.go_to_cart()

    return {
        "cart": cart,
        "unit_price": unit_price,
    }


# ==========================================================
# THEN - VERIFY PRODUCT AND QUANTITY
# ==========================================================

@then(
    parsers.parse(
        'the cart should contain "{product}" '
        "with quantity {quantity:d}"
    )
)
def verify_cart_product(cart_context, product, quantity):

    cart = cart_context["cart"]

    # Verify product name
    expect(cart.product_titles).to_contain_text(product)

    # Verify cart quantity
    expect(cart.cart_quantity).to_have_text(
        str(quantity)
    )


# ==========================================================
# THEN - VERIFY PRODUCT LINE PRICE
# ==========================================================

@then(
    parsers.parse(
        "the cart line price should equal "
        "the unit price multiplied by {quantity:d}"
    )
)
def verify_line_price(cart_context, quantity):

    cart = cart_context["cart"]

    unit_price = cart_context["unit_price"]

    # Wait for line price
    expect(cart.line_prices.first).to_be_visible()

    # Calculate expected price
    expected_price = unit_price * quantity

    # Get actual line prices
    actual_prices = cart.line_totals()

    assert actual_prices, "Cart has no product line"

    assert actual_prices[0] == pytest.approx(
        expected_price,
        abs=0.01
    )


# ==========================================================
# THEN - VERIFY CART TOTAL
# ==========================================================

@then(
    "the cart total should equal the sum of line prices"
)
def verify_cart_total(cart_context):

    cart = cart_context["cart"]

    # Wait for total
    expect(cart.total).to_be_visible()

    # Calculate expected total
    line_prices = cart.line_totals()

    assert line_prices, "Cart has no product lines"

    expected_total = sum(line_prices)

    actual_total = cart.total_value()

    assert actual_total == pytest.approx(
        expected_total,
        abs=0.01
    )
