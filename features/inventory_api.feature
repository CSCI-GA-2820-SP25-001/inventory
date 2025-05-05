Feature: Inventory API Functional Scenarios
  This feature tests the core functionality of the inventory microservice via its RESTful API.

  Scenario: List all products
    Given the inventory has multiple products
    When I send a GET request to "/inventory"
    Then I should receive a 200 OK response
    And the response should include a list of all products

  Scenario: Create a new product
    Given I have a valid product payload
    When I send a POST request to "/inventory" with the product data
    Then the product should be created
    And I should receive a 201 Created response

  Scenario: Retrieve a product by ID
    Given a product exists with ID 123
    When I send a GET request to "/inventory/123"
    Then I should receive a 200 OK response with the product details

  Scenario: Update a product’s quantity
    Given a product exists with ID 123
    When I send a PUT request to "/inventory/123" with updated quantity
    Then I should receive a 200 OK response
    And the quantity should be updated

  Scenario: Delete a product
    Given a product exists with ID 123
    When I send a DELETE request to "/inventory/123"
    Then the product should be removed from the system
    And I should receive a 204 No Content response

  Scenario: Filter products by condition
    Given products exist with different conditions
    When I send a GET request to "/inventory?condition=used"
    Then I should receive a 200 OK response
    And only products with condition "used" should be returned

  Scenario: Mark a product as Needs Restock
    Given a product exists with ID 123 and its quantity is below the restock level
    When I send a PUT request to "/inventory/123/restock"
    Then I should receive a 200 OK response
    And the product should be marked as "Needs Restock"

  Scenario: Mark a product as Damaged
    Given a product exists with ID 123
    When I send a PUT request to "/inventory/123/damage"
    Then I should receive a 200 OK response
    And the product should be marked as "Damaged"
