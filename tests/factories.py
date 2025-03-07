"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Inventory


class InventoryFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Inventory

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    quantity = factory.Faker("random_int", min=0, max=100)
    condition = factory.Faker("condition")
    restock_level = factory.Faker("random_int", min=0, max=100)

    # Todo: Add your other attributes here...
