
"""
Sprint 2 - Additional UI Tests.

Six additional tests:
1. Search hammer products.
2. Product details are displayed.
3. Product quantity can be changed.
4. Cart displays the added product.
5. Authenticated account page is accessible.
6. Contact form fields are available.

Run:
    pytest tests/ui/test_sprint2.py -vv
"""

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.account_page import AccountPage
from pages.contact_page import ContactPage


pytestmark = pytest.mark.ui


# ---------------------------------------------------------
# GROUP 1: PRODUCT SEARCH
# ---------------------------------------------------------

def test_ui_search_hammer_filters_results(page):
    """
    Goal: Verify search filters products by keyword.
    Expected: All displayed products contain 'hammer'.
    """

    home = HomePage(page).open().search("hammer")

    expect(home.search_completed).to_be_visible()
    expect(home.search_caption).to_contain_text("hammer")

    names = home.product_names.all_inner_texts()

    assert names, "Search returned no products"

    assert all(
        "hammer" in name.casefold()
        for name in names
    ), names


# ---------------------------------------------------------
# GROUP 2: PRODUCT DETAILS
# ---------------------------------------------------------

def test_ui_product_details_display_correct_information(page):
    """
    Goal: Verify product details are displayed.
    Expected: Product name, price and add-to-cart button are visible.
    """

    product = (
        HomePage(page)
        .open()
        .open_product("Claw Hammer")
    )

    expect(product.name).to_have_text("Claw Hammer")

    expect(product.unit_price).to_be_visible()

    assert product.unit_price.inner_text().strip(), (
        "Product price is empty"
    )

    expect(product.add_to_cart_button).to_be_visible()
    expect(product.add_to_cart_button).to_be_enabled()


def test_ui_product_quantity_can_be_changed(page):
    """
    Goal: Verify the product quantity can be changed.
    Expected: Quantity field accepts the value 2.
    """

    product = (
        HomePage(page)
        .open()
        .open_product("Claw Hammer")
    )

    expect(product.quantity).to_be_visible()

    product.quantity.fill("2")

    expect(product.quantity).to_have_value("2")


# ---------------------------------------------------------
# GROUP 3: SHOPPING CART
# ---------------------------------------------------------

def test_ui_cart_displays_added_product(page):
    """
    Goal: Verify the cart displays an added product.
    Expected: Claw Hammer and cart total are visible.
    """

    product = (
        HomePage(page)
        .open()
        .open_product("Claw Hammer")
    )

    product.add_to_cart(quantity=2)

    expect(product.toast).to_contain_text(
        "Product added to shopping cart"
    )

    expect(product.cart_quantity).to_have_text("2")

    cart = product.go_to_cart()

    expect(cart.product_titles).to_contain_text(
        "Claw Hammer"
    )

    expect(cart.total).to_be_visible()


# ---------------------------------------------------------
# GROUP 4: AUTHENTICATION AND ACCOUNT
# ---------------------------------------------------------

def test_ui_authenticated_user_can_open_account(logged_in_page):
    """
    Goal: Verify an authenticated user can access the account page.
    Precondition: logged_in_page uses saved storage_state.
    Expected: My account title and QA Bot user menu are visible.
    """

    account = AccountPage(logged_in_page).open()

    expect(account.title).to_have_text("My account")

    expect(account.nav_menu).to_contain_text("QA Bot")


# ---------------------------------------------------------
# GROUP 5: CONTACT FORM
# ---------------------------------------------------------

def test_ui_contact_form_fields_are_available(page):
    """
    Goal: Verify all contact form fields are available.
    Expected: Fields are visible and can accept user input.
    """

    contact = ContactPage(page).open()

    # Verify form fields
    expect(contact.first_name).to_be_visible()
    expect(contact.last_name).to_be_visible()
    expect(contact.email).to_be_visible()
    expect(contact.subject).to_be_visible()
    expect(contact.message).to_be_visible()
    expect(contact.submit_button).to_be_visible()

    # Fill form fields
    contact.first_name.fill("Sprint")
    contact.last_name.fill("Tester")
    contact.email.fill("sprint2@example.com")
    contact.message.fill("Testing contact form in Sprint 2")

    # Verify entered values
    expect(contact.first_name).to_have_value("Sprint")
    expect(contact.last_name).to_have_value("Tester")
    expect(contact.email).to_have_value("sprint2@example.com")
    expect(contact.message).to_have_value(
        "Testing contact form in Sprint 2"
    )
