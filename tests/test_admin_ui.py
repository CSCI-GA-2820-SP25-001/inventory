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
from service.models import db, Inventory, Alert
from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@postgres:5432/testdb"
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
        db.session.query(Alert).delete()  # clean up alerts first due to foreign key
        db.session.query(Inventory).delete()  # clean up the inventory
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_admin_ui_page(self):
        """It should return the admin UI page"""
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Inventory Management System", response.data)
        self.assertIn(b"Product Search", response.data)
        self.assertIn(b"Add New Product", response.data)

    def test_update_stock_endpoint(self):
        """It should update stock level and create alert if below restock level"""
        # Create a test product
        test_product = InventoryFactory(
            name="Test Product", quantity=10, condition="new", restock_level=5
        )
        test_product.create()

        # Update stock to below restock level
        update_data = {"quantity": 3}
        response = self.client.put(
            f"/inventory/{test_product.id}/restock_check",
            json=update_data,
            content_type="application/json",
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(int(data["quantity"]), 3)

        # Verify alert was created
        alerts = db.session.query(Alert).filter_by(product_id=test_product.id).all()
        self.assertEqual(len(alerts), 1)
        self.assertIn("Low Stock Alert", alerts[0].message)
        self.assertIn(str(test_product.name), alerts[0].message)

    def test_update_stock_no_alert(self):
        """It should update stock level without creating alert if above restock level"""
        # Create a test product
        test_product = InventoryFactory(
            name="Test Product", quantity=10, condition="new", restock_level=5
        )
        test_product.create()

        # Update stock to above restock level
        update_data = {"quantity": 8}
        response = self.client.put(
            f"/inventory/{test_product.id}/restock_check",
            json=update_data,
            content_type="application/json",
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["quantity"], 8)

        # Verify no alert was created
        alerts = db.session.query(Alert).filter_by(product_id=test_product.id).all()
        self.assertEqual(len(alerts), 0)

    def test_update_stock_not_found(self):
        """It should return 404 when updating stock for non-existent inventory"""
        update_data = {"quantity": 8}
        response = self.client.put(
            "/inventory/9999/restock_check",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_update_stock_missing_quantity(self):
        """It should return 400 when quantity is missing"""
        # Create a test product
        test_product = InventoryFactory(
            name="Test Product", quantity=10, condition="new", restock_level=5
        )
        test_product.create()

        # Update with missing quantity
        update_data = {"not_quantity": 8}
        response = self.client.put(
            f"/inventory/{test_product.id}/restock_check",
            json=update_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_find_by_category(self):
        """It should handle find_by_category even though it's not implemented"""
        # This tests the code path in list_inventory that calls find_by_category
        response = self.client.get("/inventory?category=electronics")
        self.assertEqual(response.status_code, 200)
        # Since find_by_category is not implemented, it should return an empty list
        self.assertEqual(response.get_json(), [])


if __name__ == "__main__":
    unittest.main()
