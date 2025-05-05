"""
Environment setup for behave tests
"""

import os
import threading
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from wsgi import app
from service.models import db, Inventory
from tests.factories import InventoryFactory

# Database URI for testing
# Use SQLite for testing to avoid requiring PostgreSQL
DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///test_admin.db")

# Flask app thread
flask_thread = None


def before_all(context):
    """Setup before all tests"""
    # Configure Flask app
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.logger.setLevel(logging.CRITICAL)
    app.app_context().push()

    # Start Flask app in a separate thread
    def run_flask_app():
        app.run(host="localhost", port=5000, use_reloader=False)

    global flask_thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # Give the server a moment to start
    time.sleep(1)

    # Set up browser driver (Chrome by default, can be configured via environment variable)
    browser = os.getenv("BROWSER", "chrome").lower()

    if browser == "firefox":
        options = webdriver.FirefoxOptions()
        if os.getenv("HEADLESS", "true").lower() == "true":
            options.add_argument("--headless")
        service = FirefoxService(GeckoDriverManager().install())
        context.driver = webdriver.Firefox(service=service, options=options)
    else:  # Default to Chrome
        options = webdriver.ChromeOptions()
        if os.getenv("HEADLESS", "true").lower() == "true":
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = ChromeService(ChromeDriverManager().install())
        context.driver = webdriver.Chrome(service=service, options=options)

    # Set implicit wait time
    context.driver.implicitly_wait(10)

    # Store the base URL
    context.base_url = "http://localhost:5000"


def before_scenario(context, scenario):
    """Setup before each scenario"""
    # Clean up the database
    db.session.query(Inventory).delete()
    db.session.commit()

    # Create a test product for testing
    test_product = InventoryFactory(
        name="Test Product", quantity=10, condition="new", restock_level=5
    )
    test_product.create()

    # Store the test product in the context
    context.test_product = test_product


def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    # Clean up the database
    db.session.query(Inventory).delete()
    db.session.commit()


def after_all(context):
    """Cleanup after all tests"""
    # Close the browser
    if hasattr(context, "driver") and context.driver:
        context.driver.quit()

    # Close the database session
    db.session.close()
