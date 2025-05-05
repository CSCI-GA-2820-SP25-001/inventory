Feature: Admin UI Functionality
  As a QA Engineer
  I need to test the Admin UI functionality
  So that I can ensure it works correctly for users

  Background:
    Given the Admin UI is running
    And a test product exists in the inventory

  Scenario: Search for a product
    When I search for the product by ID
    Then I should see the product details displayed
    And the product name should be correct
    And the product quantity should be correct
    And the product condition should be correct
    And the product restock level should be correct

  Scenario: Edit a product
    When I search for the product by ID
    And I click the edit button
    Then I should see the update form
    And the form should be pre-populated with the current values

  Scenario: Update a product
    When I search for the product by ID
    And I click the edit button
    And I update the product quantity to "15"
    And I update the product condition to "used"
    And I update the product restock level to "8"
    And I click the update button
    Then I should see a success message
    And the product details should be updated with the new values

  Scenario: Cancel product update
    When I search for the product by ID
    And I click the edit button
    And I click the cancel button
    Then the update form should be hidden
    And the product details should remain unchanged

  Scenario: Add a new product
    When I enter a new product name "Test BDD Product"
    And I enter a quantity of "20"
    And I select a condition of "new"
    And I enter a restock level of "10"
    And I click the add product button
    Then I should see a success message for the new product
    And I should be able to search for the new product
