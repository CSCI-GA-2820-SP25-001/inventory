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
Inventory Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Inventory
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Inventory
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Welcome to the Inventory REST API Service",
            version="1.0",
            paths=url_for("list_inventory", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW INVENTORY
######################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Create Inventory
    This endpoint will create Inventory based the data in the body that is posted
    """
    app.logger.info("Request to Create Inventory...")
    check_content_type("application/json")

    inventory = Inventory()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    inventory.deserialize(data)

    # Save the new Inventory to the database
    inventory.create()
    app.logger.info("Inventory with new id [%s] saved!", inventory.id)

    # Return the location of the new Inventory
    # To Do: Uncomment this code when "get_inventory" is implemented
    location_url = url_for("get_inventory", inventory_id=inventory.id, _external=True)
    # location_url = "unknown"
    return (
        jsonify(inventory.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# UPDATE AN EXISTING INVENTORY
######################################################################
@app.route("/inventory/<int:inventory_id>", methods=["PUT"])
def update_inventory(inventory_id):
    """
    Update a Inventory

    This endpoint will update a Inventory based the body that is posted
    """
    app.logger.info("Request to Update a inventory with id [%s]", inventory_id)
    check_content_type("application/json")

    # Attempt to find the Inventory and abort if not found
    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' was not found.",
        )

    # Update the Inventory with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    inventory.deserialize(data)

    # Save the updates to the database
    inventory.update()

    app.logger.info("Inventory with ID: %d updated.", inventory.id)
    return jsonify(inventory.serialize()), status.HTTP_200_OK


######################################################################
# READ AN INVENTORY
######################################################################


@app.route("/inventory/<int:inventory_id>", methods=["GET"])
def get_inventory(inventory_id):
    """
    Retrieve a single Inventory

    This endpoint will return a Inventory based on it's id
    """
    app.logger.info("Request to Retrieve a inventory with id [%s]", inventory_id)

    # Attempt to find the Inventory and abort if not found
    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' was not found.",
        )

    app.logger.info("Returning inventory: %s", inventory.name)
    return jsonify(inventory.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN INVENTORY
######################################################################
@app.route("/inventory/<int:inventory_id>", methods=["DELETE"])
def delete_inventory(inventory_id):
    """
    Delete a Inventory

    This endpoint will delete a Inventory based the id specified in the path
    """
    app.logger.info("Request to Delete a inventory with id [%s]", inventory_id)

    # Delete the Inventory if it exists
    inventory = Inventory.find(inventory_id)
    if inventory:
        app.logger.info("Inventory with ID: %d found.", inventory.id)
        inventory.delete()

    app.logger.info("Inventory with ID: %d delete complete.", inventory_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL INVENTORY
######################################################################
@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Returns all of the Inventory"""
    app.logger.info("Request for inventory list")

    inventory = []

    # Parse any arguments from the query string
    category = request.args.get("category")
    name = request.args.get("name")

    if category:
        app.logger.info("Find by category: %s", category)
        inventory = Inventory.find_by_category(category)
    elif name:
        app.logger.info("Find by name: %s", name)
        inventory = Inventory.find_by_name(name)
    else:
        app.logger.info("Find all")
        inventory = Inventory.all()

    results = [inventory.serialize() for inventory in inventory]
    app.logger.info("Returning %d inventory", len(results))
    return jsonify(results), status.HTTP_200_OK
