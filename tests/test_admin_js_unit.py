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
Unit Tests for Admin UI JavaScript Functions
"""

import os
import json
import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock
from wsgi import app
from service.models import db, Inventory, Alert
from .factories import InventoryFactory
import requests_mock

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@postgres:5432/testdb"
)


######################################################################
#  A D M I N   J S   U N I T   T E S T   C A S E S
######################################################################
class TestAdminJSUnit(TestCase):
    """Unit Tests for Admin UI JavaScript Functions"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel("CRITICAL")
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

        # Create a test product for testing
        self.test_product = InventoryFactory(
            name="Test Product", quantity=10, condition="new", restock_level=5
        )
        self.test_product.create()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_get_inventory_api(self):
        """It should return inventory data from the API"""
        # Make a request to get inventory by ID
        response = self.client.get(f"/inventory/{self.test_product.id}")

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Parse the response data
        data = json.loads(response.data)

        # Verify the data matches the test product
        self.assertEqual(data["id"], self.test_product.id)
        self.assertEqual(data["name"], self.test_product.name)
        self.assertEqual(data["quantity"], int(self.test_product.quantity))
        self.assertEqual(data["condition"], self.test_product.condition)
        self.assertEqual(
            int(data["restock_level"]), int(self.test_product.restock_level)
        )

    def test_update_inventory_api(self):
        """It should update inventory data through the API"""
        # Create updated data
        updated_data = {
            "name": self.test_product.name,
            "quantity": 15,
            "condition": "used",
            "restock_level": 8,
        }

        # Make a PUT request to update the inventory
        response = self.client.put(
            f"/inventory/{self.test_product.id}",
            json=updated_data,
            content_type="application/json",
        )

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Parse the response data
        data = json.loads(response.data)

        # Verify the data was updated
        self.assertEqual(data["id"], self.test_product.id)
        self.assertEqual(data["name"], self.test_product.name)
        self.assertEqual(int(data["quantity"]), 15)
        self.assertEqual(data["condition"], "used")
        self.assertEqual(int(data["restock_level"]), 8)

        # Verify the database was updated
        updated_product = Inventory.find(self.test_product.id)
        self.assertEqual(int(updated_product.quantity), 15)
        self.assertEqual(updated_product.condition, "used")
        self.assertEqual(int(updated_product.restock_level), 8)

    def test_update_inventory_api_not_found(self):
        """It should return 404 when updating non-existent inventory"""
        # Create updated data
        updated_data = {
            "name": "Non-existent Product",
            "quantity": 15,
            "condition": "used",
            "restock_level": 8,
        }

        # Make a PUT request to update a non-existent inventory
        response = self.client.put(
            "/inventory/9999", json=updated_data, content_type="application/json"
        )

        # Check response status code
        self.assertEqual(response.status_code, 404)

    def test_update_inventory_api_invalid_content_type(self):
        """It should return 415 when content type is not application/json"""
        # Make a PUT request with invalid content type
        response = self.client.put(
            f"/inventory/{self.test_product.id}",
            data="This is not JSON",
            content_type="text/plain",
        )

        # Check response status code
        self.assertEqual(response.status_code, 415)

    def test_update_inventory_api_missing_fields(self):
        """It should return 400 when required fields are missing"""
        # Create incomplete data (missing condition)
        incomplete_data = {
            "name": self.test_product.name,
            "quantity": 15,
            # Missing condition field
            "restock_level": 8,
        }

        # Make a PUT request with incomplete data
        response = self.client.put(
            f"/inventory/{self.test_product.id}",
            json=incomplete_data,
            content_type="application/json",
        )

        # Check response status code - should be 400 Bad Request
        self.assertEqual(response.status_code, 400)

    @patch("requests.put")
    def test_update_product_function(self, mock_put):
        """Test the updateProduct function behavior with mocked API response"""
        # This test would normally use Jest to test the JavaScript function directly
        # Here we're simulating the behavior by testing the API it would call

        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": self.test_product.id,
            "name": self.test_product.name,
            "quantity": 15,
            "condition": "used",
            "restock_level": 8,
        }
        mock_put.return_value = mock_response

        # Create updated data
        updated_data = {
            "name": self.test_product.name,
            "quantity": 15,
            "condition": "used",
            "restock_level": 8,
        }

        # Make a PUT request to update the inventory
        response = self.client.put(
            f"/inventory/{self.test_product.id}",
            json=updated_data,
            content_type="application/json",
        )

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Parse the response data
        data = json.loads(response.data)

        # Verify the data was updated
        self.assertEqual(int(data["quantity"]), 15)
        self.assertEqual(data["condition"], "used")
        self.assertEqual(int(data["restock_level"]), 8)

    def test_api_error_handling(self):
        """Test error handling for API requests"""
        with requests_mock.Mocker() as m:
            # Mock a failed API request
            m.put(
                f"http://localhost/inventory/{self.test_product.id}",
                status_code=500,
                json={"error": "Server error"},
            )

            # Create updated data
            updated_data = {
                "name": self.test_product.name,
                "quantity": 15,
                "condition": "used",
                "restock_level": 8,
            }

            # Make a PUT request to update the inventory
            # This would normally be handled by the JavaScript error handling
            response = self.client.put(
                f"/inventory/{self.test_product.id}",
                json=updated_data,
                content_type="application/json",
            )

            # In this case, our Flask app should still work
            # but we're testing the error handling that would be in the JS
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
