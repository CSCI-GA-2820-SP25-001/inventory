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
Test cases for Inventory Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Inventory, DataValidationError, db, Alert
from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  INVENTORY   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestInventory(TestCase):
    """Test Cases for Inventory Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Alert).delete()  # clean up alerts first due to foreign key
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_inventory(self):
        """It should create a Inventory"""
        inventory = InventoryFactory()
        inventory.create()
        self.assertIsNotNone(inventory.id)
        found = Inventory.all()
        self.assertEqual(len(found), 1)
        data = Inventory.find(inventory.id)
        self.assertEqual(data.name, inventory.name)
        self.assertEqual(data.quantity, inventory.quantity)
        self.assertEqual(data.condition, inventory.condition)
        self.assertEqual(data.restock_level, inventory.restock_level)

    def test_update_a_inventory(self):
        """It should Update a Inventory"""
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.id = None
        inventory.create()
        logging.debug(inventory)
        self.assertIsNotNone(inventory.id)
        # Change it an save it
        inventory.category = "k9"
        original_id = inventory.id
        inventory.update()
        self.assertEqual(inventory.id, original_id)
        self.assertEqual(inventory.category, "k9")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0].id, original_id)
        self.assertEqual(inventory[0].category, "k9")

    def test_update_no_id(self):
        """It should not Update a Inventory with no id"""
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.id = None
        self.assertRaises(DataValidationError, inventory.update)

    def test_serialize_inventory(self):
        """It should serialize an Inventory"""
        inventory = InventoryFactory()
        data = inventory.serialize()
        self.assertIsInstance(data, dict)
        self.assertIn("id", data)
        self.assertEqual(data["name"], inventory.name)

    def test_deserialize_inventory(self):
        """It should deserialize an Inventory"""
        inventory = Inventory()
        data = InventoryFactory().serialize()
        inventory.deserialize(data)
        self.assertEqual(inventory.name, data["name"])
        self.assertEqual(inventory.quantity, data["quantity"])

    def test_deserialize_missing_data(self):
        """It should raise error for missing data"""
        inventory = Inventory()
        data = {"name": "Item"}  # missing fields
        with self.assertRaises(DataValidationError):
            inventory.deserialize(data)

    def test_deserialize_bad_data(self):
        """It should raise error for bad data"""
        inventory = Inventory()
        with self.assertRaises(DataValidationError):
            inventory.deserialize("bad data")

    def test_update_inventory_without_id(self):
        """It should raise error when updating without id"""
        inventory = InventoryFactory()
        inventory.id = None
        with self.assertRaises(DataValidationError):
            inventory.update()

    def test_repr_string(self):
        """It should return a string representation"""
        inventory = InventoryFactory()
        self.assertTrue(str(inventory).startswith("<Inventory"))
