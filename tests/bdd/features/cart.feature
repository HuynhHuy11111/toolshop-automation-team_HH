
Feature: Shopping cart

  As a shopper
  I want to add products to my shopping cart with a chosen quantity
  So that I can verify the product price and cart total

  Background:
    Given I am on the home page

  Scenario Outline: Shopper adds a product to the shopping cart
    When I open the product "<product>"
    And I add it to the cart with quantity <quantity>
    Then the cart should contain "<product>" with quantity <quantity>
    And the cart line price should equal the unit price multiplied by <quantity>
    And the cart total should equal the sum of line prices

    Examples:
      | product            | quantity |
      | Combination Pliers | 1        |
      | Claw Hammer        | 2        |
