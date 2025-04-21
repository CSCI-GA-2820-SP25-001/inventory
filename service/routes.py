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

from flask import jsonify, request, url_for, abort, render_template
from flask import current_app as app  # Import Flask application
from service.models import Inventory, Alert, db
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
    ...
    condition = request.args.get("condition")
    category = request.args.get("category")
    name = request.args.get("name")

    if condition:
        app.logger.info("Find by condition: %s", condition)
        inventory = Inventory.find_by_condition(condition)
    elif category:
        inventory = Inventory.find_by_category(category)
    elif name:
        inventory = Inventory.find_by_name(name)
    else:
        inventory = Inventory.all()

    results = [item.serialize() for item in inventory]
    app.logger.info("Returning %d inventory", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# ACTION: MARK INVENTORY AS DAMAGED
######################################################################
@app.route("/inventory/<int:inventory_id>/mark_damaged", methods=["PUT"])
def mark_damaged(inventory_id):
    """
    Marks an Inventory as damaged
    """
    app.logger.info("Request to mark inventory as damaged [%s]", inventory_id)

    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND, f"Inventory with id '{inventory_id}' not found"
        )

    inventory.condition = "damaged"
    inventory.update()

    app.logger.info("Inventory with ID: %d marked as damaged.", inventory.id)
    return jsonify(inventory.serialize()), status.HTTP_200_OK


######################################################################
# health-endpoint
# HEALTH
######################################################################
@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="OK"), 200


# Trigger restock
######################################################################


@app.route("/inventory/<int:inventory_id>/restock_check", methods=["PUT"])
def update_stock(inventory_id):
    inventory = Inventory.find(inventory_id)
    if not inventory:
        return jsonify({"error": "Inventory not found"}), 404

    data = request.get_json()
    if "quantity" not in data:
        return jsonify({"error": "Missing quantity"}), 400

    new_quantity = data["quantity"]
    inventory.quantity = new_quantity

    # Check for low stock
    if new_quantity < inventory.restock_level:
        message = (
            f"Low Stock Alert: Item '{inventory.name}' has quantity {new_quantity}, "
            f"below restock level {inventory.restock_level}"
        )
        alert = Alert(product_id=inventory.id, message=message)
        db.session.add(alert)

    inventory.update()
    db.session.commit()
    return jsonify(inventory.serialize()), 200


# Endpoint for reading stock
# I acknowledge it that the code would be much cleaner if the above function would refer to the below function.
@app.route("/inventory/stock", methods=["GET"])
def get_stock_levels():
    """
    Retrieve stock levels for all inventory items
    """
    app.logger.info("Request to retrieve inventory stock levels")
    inventory_items = Inventory.all()
    stock_levels = [
        {"product_id": item.id, "quantity": item.quantity} for item in inventory_items
    ]
    return jsonify(stock_levels), status.HTTP_200_OK


# Endpoint for Low Stock Alert
@app.route("/inventory/low-stock", methods=["GET"])
def get_low_stock_alerts():
    """
    Retrieve low-stock alerts for inventory items
    """
    app.logger.info("Request to retrieve low-stock alerts")
    inventory_items = Inventory.all()
    low_stock_items = [
        {
            "product_id": item.id,
            "quantity": item.quantity,
            "restock_level": item.restock_level,
            "alert_status": "Alert! Product is Low Stock",
        }
        for item in inventory_items
        if int(item.quantity) < int(item.restock_level)
    ]
    return jsonify(low_stock_items), status.HTTP_200_OK


######################################################################
# ADMIN UI ROUTES
######################################################################


@app.route("/admin", methods=["GET"])
def admin_ui():
    """
    Admin UI for Inventory Management
    This endpoint will render the Admin UI page
    """
    app.logger.info("Request for Admin UI page")
    return render_template("admin.html")
