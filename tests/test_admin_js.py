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
Test cases for Admin UI JavaScript functionality
"""

import os
import logging
import unittest
import threading
from unittest import TestCase
from wsgi import app
from service.models import db, Inventory
from .factories import InventoryFactory
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  A D M I N   J S   T E S T   C A S E S
######################################################################
class TestAdminJS(TestCase):
    """Test Cases for Admin UI JavaScript functionality"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

        # Start Flask app in a separate thread
        def run_flask_app():
            app.run(host="localhost", port=5000, use_reloader=False)

        cls.flask_thread = threading.Thread(target=run_flask_app)
        cls.flask_thread.daemon = True
        cls.flask_thread.start()

        # Give the server a moment to start
        time.sleep(1)

        # Set up Chrome options for headless testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Create a new instance of the Chrome driver
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            cls.driver = None
            print(f"Chrome driver could not be initialized: {str(e)}")

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()
        if cls.driver:
            cls.driver.quit()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        self.client.testing = True
        db.session.query(Inventory).delete()  # clean up the inventory
        db.session.commit()

        # Skip tests if driver is not available
        if not self.__class__.driver:
            self.skipTest("Chrome driver not available")

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

    def test_search_product(self):
        """It should search for a product and display its details"""
        # Start the Flask app
        with app.test_client():
            # Navigate to the admin page
            self.driver.get("http://localhost:5000/admin")

            # Find the product ID input and search button
            product_id_input = self.driver.find_element(By.ID, "product-id")
            search_btn = self.driver.find_element(By.ID, "search-btn")

            # Enter the product ID and click search
            product_id_input.send_keys(str(self.test_product.id))
            search_btn.click()

            # Wait for the product details to be displayed
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "product-details"))
            )

            # Verify the product details are displayed correctly
            product_name = self.driver.find_element(By.ID, "product-name").text
            product_id = self.driver.find_element(By.ID, "product-id-display").text
            product_quantity = self.driver.find_element(By.ID, "product-quantity").text
            product_condition = self.driver.find_element(
                By.ID, "product-condition"
            ).text
            product_restock_level = self.driver.find_element(
                By.ID, "product-restock-level"
            ).text

            self.assertEqual(product_name, self.test_product.name)
            self.assertEqual(product_id, str(self.test_product.id))
            self.assertEqual(product_quantity, str(self.test_product.quantity))
            self.assertEqual(product_condition, self.test_product.condition)
            self.assertEqual(
                product_restock_level, str(self.test_product.restock_level)
            )

    def test_edit_product_button(self):
        """It should show the update form when edit button is clicked"""
        # Start the Flask app
        with app.test_client():
            # Navigate to the admin page
            self.driver.get("http://localhost:5000/admin")

            # Find the product ID input and search button
            product_id_input = self.driver.find_element(By.ID, "product-id")
            search_btn = self.driver.find_element(By.ID, "search-btn")

            # Enter the product ID and click search
            product_id_input.send_keys(str(self.test_product.id))
            search_btn.click()

            # Wait for the product details to be displayed
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "product-details"))
            )

            # Click the edit button
            edit_btn = self.driver.find_element(By.ID, "edit-product-btn")
            edit_btn.click()

            # Wait for the update form to be displayed
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "update-product-section"))
            )

            # Verify the update form is displayed and pre-populated with current values
            update_quantity = self.driver.find_element(
                By.ID, "update-product-quantity"
            ).get_attribute("value")
            update_condition = self.driver.find_element(
                By.ID, "update-product-condition"
            ).get_attribute("value")
            update_restock_level = self.driver.find_element(
                By.ID, "update-product-restock-level"
            ).get_attribute("value")

            self.assertEqual(update_quantity, str(self.test_product.quantity))
            self.assertEqual(update_condition, self.test_product.condition)
            self.assertEqual(update_restock_level, str(self.test_product.restock_level))

    def test_cancel_update(self):
        """It should hide the update form when cancel button is clicked"""
        # Start the Flask app
        with app.test_client():
            # Navigate to the admin page
            self.driver.get("http://localhost:5000/admin")

            # Find the product ID input and search button
            product_id_input = self.driver.find_element(By.ID, "product-id")
            search_btn = self.driver.find_element(By.ID, "search-btn")

            # Enter the product ID and click search
            product_id_input.send_keys(str(self.test_product.id))
            search_btn.click()

            # Wait for the product details to be displayed
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "product-details"))
            )

            # Click the edit button
            edit_btn = self.driver.find_element(By.ID, "edit-product-btn")
            edit_btn.click()

            # Wait for the update form to be displayed
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "update-product-section"))
            )

            # Click the cancel button
            cancel_btn = self.driver.find_element(By.ID, "cancel-update-btn")
            cancel_btn.click()

            # Verify the update form is hidden
            time.sleep(1)  # Give time for the UI to update
            update_section = self.driver.find_element(By.ID, "update-product-section")
            self.assertFalse(update_section.is_displayed())

    def test_update_product(self):
        """It should update a product with new values"""
        # Test updating a product directly through the API
        with app.test_client() as client:
            # Create updated data
            updated_data = {
                "name": self.test_product.name,
                "quantity": 15,
                "condition": "used",
                "restock_level": 8,
            }

            # Make a PUT request to update the inventory
            response = client.put(
                f"/inventory/{self.test_product.id}",
                json=updated_data,
                content_type="application/json",
            )

            # Check response status code
            self.assertEqual(response.status_code, 200)

            # Verify the database was updated
            updated_product = Inventory.find(self.test_product.id)
            self.assertEqual(updated_product.quantity, 15)
            self.assertEqual(updated_product.condition, "used")
            self.assertEqual(updated_product.restock_level, 8)

            # Now test the UI functionality
            # Navigate to the admin page
            self.driver.get("http://localhost:5000/admin")

            # Find the product ID input and search button
            product_id_input = self.driver.find_element(By.ID, "product-id")
            search_btn = self.driver.find_element(By.ID, "search-btn")

            # Enter the product ID and click search
            product_id_input.send_keys(str(self.test_product.id))
            search_btn.click()

            # Wait for the product details to be displayed
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "product-details"))
            )

            # Verify the UI shows the updated values
            product_quantity = self.driver.find_element(By.ID, "product-quantity").text
            product_condition = self.driver.find_element(
                By.ID, "product-condition"
            ).text
            product_restock_level = self.driver.find_element(
                By.ID, "product-restock-level"
            ).text

            # The UI should reflect the updated values from the database
            self.assertEqual(product_quantity, "15")
            self.assertEqual(product_condition, "used")
            self.assertEqual(product_restock_level, "8")

    def test_update_product_validation(self):
        """It should validate form fields before updating"""
        # Start the Flask app
        with app.test_client():
            # Navigate to the admin page
            self.driver.get("http://localhost:5000/admin")

            # Find the product ID input and search button
            product_id_input = self.driver.find_element(By.ID, "product-id")
            search_btn = self.driver.find_element(By.ID, "search-btn")

            # Enter the product ID and click search
            product_id_input.send_keys(str(self.test_product.id))
            search_btn.click()

            # Wait for the product details to be displayed
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "product-details"))
            )

            # Click the edit button
            edit_btn = self.driver.find_element(By.ID, "edit-product-btn")
            edit_btn.click()

            # Wait for the update form to be displayed
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "update-product-section"))
            )

            # Clear the form fields
            update_quantity = self.driver.find_element(By.ID, "update-product-quantity")
            update_condition = self.driver.find_element(
                By.ID, "update-product-condition"
            )
            update_restock_level = self.driver.find_element(
                By.ID, "update-product-restock-level"
            )

            update_quantity.clear()
            update_condition.find_element(By.XPATH, "//option[@value='']").click()
            update_restock_level.clear()

            # Click the update button
            update_btn = self.driver.find_element(By.ID, "update-product-btn")
            update_btn.click()

            # Wait for the error message to be displayed
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "update-product-message"))
            )

            # Verify the error message is displayed
            error_message = self.driver.find_element(
                By.ID, "update-product-message"
            ).text
            self.assertEqual(error_message, "Please fill out all fields")

            # Verify the update form is still displayed
            update_section = self.driver.find_element(By.ID, "update-product-section")
            self.assertTrue(update_section.is_displayed())

            # Verify the database was not updated
            unchanged_product = Inventory.find(self.test_product.id)
            self.assertEqual(unchanged_product.quantity, self.test_product.quantity)
            self.assertEqual(unchanged_product.condition, self.test_product.condition)
            self.assertEqual(
                unchanged_product.restock_level, self.test_product.restock_level
            )


if __name__ == "__main__":
    unittest.main()
