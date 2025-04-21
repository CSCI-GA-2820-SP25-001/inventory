######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Admin UI Routes
"""

import os
import logging
import unittest
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Inventory, Alert
from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  A D M I N   U I   T E S T   C A S E S
######################################################################
class TestAdminUI(TestCase):
    """Test Cases for Admin UI Routes"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        self.client.testing = True
        db.session.query(
            Alert
        ).delete()  # clean up alerts first (foreign key constraint)
        db.session.query(Inventory).delete()  # clean up the inventory
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_get_admin_ui(self):
        """It should return the Admin UI page"""
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Inventory Management System", response.data)
        self.assertIn(b"Add New Product", response.data)
        self.assertIn(b"Product Search", response.data)

    def test_restock_check(self):
        """It should update inventory quantity and create alert if below restock level"""
        # Create a test inventory item
        test_inventory = InventoryFactory(quantity=10, restock_level=5)
        test_inventory.create()
        inventory_id = test_inventory.id

        # Test updating quantity above restock level
        data = {"quantity": 8}
        response = self.client.put(
            f"/inventory/{inventory_id}/restock_check",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_inventory = response.get_json()
        self.assertEqual(updated_inventory["quantity"], 8)

        # Verify no alerts were created
        alerts = db.session.query(Alert).filter_by(product_id=inventory_id).all()
        self.assertEqual(len(alerts), 0)

        # Test updating quantity below restock level
        data = {"quantity": 3}
        response = self.client.put(
            f"/inventory/{inventory_id}/restock_check",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_inventory = response.get_json()
        self.assertEqual(updated_inventory["quantity"], 3)

        # Verify an alert was created
        alerts = db.session.query(Alert).filter_by(product_id=inventory_id).all()
        self.assertEqual(len(alerts), 1)
        self.assertIn("Low Stock Alert", alerts[0].message)

    def test_restock_check_not_found(self):
        """It should return 404 when inventory item doesn't exist"""
        data = {"quantity": 5}
        response = self.client.put(
            "/inventory/9999/restock_check", json=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        error_response = response.get_json()
        self.assertIn("error", error_response)
        self.assertEqual(error_response["error"], "Inventory not found")

    def test_restock_check_missing_quantity(self):
        """It should return 400 when quantity is missing from request"""
        # Create a test inventory item
        test_inventory = InventoryFactory()
        test_inventory.create()
        inventory_id = test_inventory.id

        # Test with missing quantity
        data = {"some_other_field": "value"}
        response = self.client.put(
            f"/inventory/{inventory_id}/restock_check",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_response = response.get_json()
        self.assertIn("error", error_response)
        self.assertEqual(error_response["error"], "Missing quantity")

    def test_update_product(self):
        """It should update a product with new values"""
        # Create a test inventory item
        test_inventory = InventoryFactory(
            name="Test Product", quantity=10, condition="new", restock_level=5
        )
        test_inventory.create()
        inventory_id = test_inventory.id

        # Update the product with new values
        updated_data = {
            "name": "Test Product",  # Keep the same name
            "quantity": 15,
            "condition": "used",
            "restock_level": 8,
        }
        response = self.client.put(
            f"/inventory/{inventory_id}",
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the response data
        updated_product = response.get_json()
        self.assertEqual(updated_product["name"], "Test Product")
        self.assertEqual(updated_product["quantity"], 15)
        self.assertEqual(updated_product["condition"], "used")
        self.assertEqual(updated_product["restock_level"], 8)

        # Verify the database was updated
        updated_inventory = Inventory.find(inventory_id)
        self.assertEqual(updated_inventory.quantity, 15)
        self.assertEqual(updated_inventory.condition, "used")
        self.assertEqual(updated_inventory.restock_level, 8)

    def test_update_product_not_found(self):
        """It should return 404 when trying to update a non-existent product"""
        # Attempt to update a product that doesn't exist
        data = {
            "name": "Non-existent Product",
            "quantity": 5,
            "condition": "new",
            "restock_level": 3,
        }
        response = self.client.put(
            "/inventory/9999", json=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_invalid_content_type(self):
        """It should return 415 when content type is not application/json"""
        # Create a test inventory item
        test_inventory = InventoryFactory()
        test_inventory.create()
        inventory_id = test_inventory.id

        # Test with invalid content type
        data = "This is not JSON"
        response = self.client.put(
            f"/inventory/{inventory_id}", data=data, content_type="text/plain"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


if __name__ == "__main__":
    unittest.main()
