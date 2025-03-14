"""
Test Factory to make fake objects for testing
"""

import factory
from factory import fuzzy
from service.models import Inventory


class InventoryFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Inventory

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    quantity = fuzzy.FuzzyInteger(0, 100)
    condition = fuzzy.FuzzyChoice(choices=("new", "used", "open_box"))
    restock_level = fuzzy.FuzzyInteger(0, 100)

    # Todo: Add your other attributes here...
