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
TestInventory API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
import unittest
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Inventory, Alert
from .factories import InventoryFactory
import pytest


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@postgres:5432/testdb"
)
BASE_URL = "/inventory"


######################################################################
#  GETTING PYTEST SETUP
######################################################################


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

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
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create inventory
    ############################################################
    def _create_inventory(self, count: int = 1) -> list:
        """Factory method to create inventory in bulk"""
        inventory = []
        for _ in range(count):
            test_inventory = InventoryFactory()
            response = self.client.post(BASE_URL, json=test_inventory.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test inventory",
            )
            new_inventory = response.get_json()
            test_inventory.id = new_inventory["id"]
            inventory.append(test_inventory)
        return inventory

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Welcome to the Inventory REST API Service")

    # create inventory test (Narissa)
    def test_create_inventory(self):
        """It should Create a new Inventory"""
        test_inventory = InventoryFactory()
        logging.debug("Test Inventory: %s", test_inventory.serialize())
        # response = self.client.post(
        #     BASE_URL, json=test_inventory.serialize(), content_type="application/json"
        # )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        logging.debug("Response status code: %s", response.status_code)
        logging.debug("Response data: %s", response.get_json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        logging.debug("Location header: %s", location)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_inventory = response.get_json()
        logging.debug("New Inventory: %s", new_inventory)
        self.assertIsNotNone(new_inventory["id"])
        self.assertEqual(new_inventory["name"], test_inventory.name)
        self.assertEqual(int(new_inventory["quantity"]), test_inventory.quantity)
        # self.assertEqual(new_inventory["quantity"], test_inventory.quantity)
        self.assertEqual(new_inventory["condition"], test_inventory.condition)
        self.assertEqual(new_inventory["restock_level"], test_inventory.restock_level)

        # To Do: Uncomment this code when "get_inventory" is implemented
        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_inventory = response.get_json()
        self.assertEqual(new_inventory["name"], test_inventory.name)
        self.assertEqual(new_inventory["quantity"], test_inventory.quantity)
        self.assertEqual(new_inventory["condition"], test_inventory.condition)
        self.assertEqual(new_inventory["restock_level"], test_inventory.restock_level)

    # update inventory test (Samir)

    def test_update_inventory(self):
        """It should Update an existing Inventory"""
        # create a inventory to update
        test_inventory = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the inventory
        new_inventory = response.get_json()
        logging.debug(new_inventory)
        new_inventory["name"] = "unknown"
        new_inventory["quantity"] = 10
        new_inventory["condition"] = "unknown"
        new_inventory["restock_level"] = 10
        response = self.client.put(
            f"{BASE_URL}/{new_inventory['id']}", json=new_inventory
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_inventory = response.get_json()
        self.assertEqual(updated_inventory["name"], "unknown")

    # Read Inventory Test (Sina)

    def test_get_inventory(self):
        """It should Get a single Inventory"""
        # get the id of a inventory
        test_inventory = self._create_inventory(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_inventory.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_inventory.name)

    def test_get_inventory_not_found(self):
        """It should not Get a Inventory thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # Delete Inventory Test (Teresa)
    def test_delete_inventory(self):
        """It should Delete a Inventory"""
        test_inventory = self._create_inventory(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_inventory.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_inventory.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_inventory(self):
        """It should Delete a Inventory even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST LIST(Teresa)
    # ----------------------------------------------------------
    def test_get_inventory_list(self):
        """It should Get a list of Inventory"""
        self._create_inventory(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # Tests

    def test_no_content_type(self):
        response = self.client.post(BASE_URL, headers={"Some-Header": "value"})
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_wrong_content_type(self):
        response = self.client.post(
            BASE_URL, data="wrong data", content_type="application/xml"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # Narissa Test Inventory by Condition
    def test_query_inventory_by_condition(self):
        """It should return inventory filtered by condition (e.g., 'new')"""

        # Create some with different conditions
        conditions = ["used", "open_box", "new", "used"]
        for cond in conditions:
            inv = InventoryFactory(condition=cond)
            self.client.post(BASE_URL, json=inv.serialize())

        # Now filter by 'new'
        response = self.client.get(f"{BASE_URL}?condition=new")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()

        self.assertGreaterEqual(len(data), 1)
        for item in data:
            self.assertEqual(item["condition"], "new")

    def test_mark_inventory_as_damaged(self):
        """It should mark an Inventory item as damaged"""
        # First create an item
        test_inventory = InventoryFactory(condition="new")
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        inventory = response.get_json()
        inventory_id = inventory["id"]

        # Mark as damaged
        response = self.client.put(f"{BASE_URL}/{inventory_id}/mark_damaged")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated = response.get_json()
        self.assertEqual(updated["condition"], "damaged")

    def test_mark_damaged_not_found(self):
        """It should return 404 when marking non-existent item as damaged"""
        response = self.client.put(f"{BASE_URL}/9999/mark_damaged")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_bad_post_request(self):
        """It should return 400 on bad POST data"""
        response = self.client.post(
            BASE_URL, data="not-json", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_not_allowed(self):
        """It should return 405 Method Not Allowed"""
        response = self.client.put("/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Sina
    # test case for inventory stock

    ################################################################
    # test case for inventory stock
    ################################################################
    def test_get_stock_levels(self):
        """It should return stock levels for all inventory items"""
        # items = self._create_inventory(3)
        response = self.client.get(f"{BASE_URL}/stock")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        # self.assertEqual(len(data), 3)
        for item in data:
            self.assertIn("product_id", item)
            self.assertIn("quantity", item)

    def test_get_stock_levels_empty(self):
        """It should return an empty list when no inventory exists"""
        response = self.client.get(f"{BASE_URL}/stock")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json(), [])

    def test_get_low_stock_alerts(self):
        """It should return products with quantity below restock level"""
        item1 = InventoryFactory(quantity=2, restock_level=5)
        # item2 = InventoryFactory(quantity=10, restock_level=5)
        response1 = self.client.post(BASE_URL, json=item1.serialize())
        # response2 = self.client.post(BASE_URL, json=item2.serialize())
        item1.id = response1.get_json()["id"]

        response = self.client.get(f"{BASE_URL}/low-stock")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_id"], item1.id)
        self.assertEqual(data[0]["alert_status"], "Alert! Product is Low Stock")

    # test case for inventory low stock
    def test_get_low_stock_alerts_empty(self):
        """It should return empty list when all stock levels are healthy"""
        item1 = InventoryFactory(quantity=10, restock_level=5)
        item2 = InventoryFactory(quantity=20, restock_level=10)
        self.client.post(BASE_URL, json=item1.serialize())
        self.client.post(BASE_URL, json=item2.serialize())

        response = self.client.get(f"{BASE_URL}/low-stock")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json(), [])


if __name__ == "__main__":
    unittest.main()


############################################################
# TEST HEALTH
############################################################
def test_health_endpoint(client):
    """Test the /health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "OK"}
