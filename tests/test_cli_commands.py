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
Test cases for CLI Commands
"""

import os
import unittest
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import db
from service.common.cli_commands import db_create

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@postgres:5432/testdb"
)


######################################################################
#  C L I   C O M M A N D S   T E S T   C A S E S
######################################################################
class TestCLICommands(TestCase):
    """Test Cases for CLI Commands"""

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
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """This runs after each test"""
        self.app_context.pop()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    # @patch("service.models.db.create_all")
    # @patch("service.models.db.drop_all")
    # def test_db_create(self, mock_drop_all, mock_create_all):
    # """It should create the database"""
    # Instead of trying to mock the Click context, let's just call the function
    # that would be called by the callback
    # from service.common.cli_commands import create_db

    # create_db()

    # mock_drop_all.assert_called_once()
    # mock_create_all.assert_called_once()


if __name__ == "__main__":
    unittest.main()
