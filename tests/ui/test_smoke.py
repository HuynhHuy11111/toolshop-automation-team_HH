
import re
import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.contact_page import ContactPage


@pytest.mark.smoke
@pytest.mark.ui
def test_smoke_search_pliers(page):
    """Goal: verify product search filters the product grid.
    Precondition: the Toolshop homepage is accessible.
    Expected: every displayed product name contains 'pliers'."""

    home = HomePage(page).open().search("pliers")

    expect(home.search_completed).to_be_visible()
    expect(home.search_caption).to_contain_text("pliers")

    names = home.product_names.all_inner_texts()

    assert names, "Search returned no products"
    assert all("pliers" in name.lower() for name in names), names


@pytest.mark.smoke
@pytest.mark.ui
def test_smoke_add_claw_hammer_quantity_three(page):
    """Goal: verify adding a product with the selected quantity.
    Precondition: the product 'Claw Hammer' exists.
    Expected: the cart badge displays quantity 3."""

    product = HomePage(page).open().open_product("Claw Hammer")

    expect(product.name).to_have_text("Claw Hammer")

    product.add_to_cart(quantity=3)

    expect(product.toast).to_contain_text(
        "Product added to shopping cart"
    )
    expect(product.cart_quantity).to_have_text("3")


@pytest.mark.smoke
@pytest.mark.ui
def test_smoke_invalid_login(page):
    """Goal: verify login rejects invalid credentials.
    Precondition: use an email address that does not exist.
    Expected: error message appears and URL ends with /auth/login."""

    login = LoginPage(page).open().login(
        "nobody-here@example.com",
        "Wrong-Password-123"
    )

    expect(login.error).to_contain_text(
        "Invalid email or password"
    )
    expect(page).to_have_url(re.compile(r"/auth/login$"))


@pytest.mark.smoke
@pytest.mark.ui
def test_smoke_empty_contact_form(page):
    """Goal: verify required-field validation on the contact form.
    Precondition: the contact form is opened with all fields empty.
    Expected: subject and message required errors are displayed."""

    contact = ContactPage(page).open()

    contact.submit()

    expect(
        contact.error_message("Subject is required")
    ).to_be_visible()

    expect(
        contact.error_message("Message is required")
    ).to_be_visible()
