"""tiferet_kb Category Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** app
from tiferet.mappers import Aggregate
from tiferet_h5.mappers import NodeObject

from ..domain import Category

# *** mappers

# ** mapper: category_aggregate
class CategoryAggregate(Category, Aggregate):
    '''
    A mutable aggregate representation of a knowledge base category.
    '''

    # * method: rename
    def rename(self, name: str) -> None:
        '''
        Rename the category.

        :param name: The new category name.
        :type name: str
        :return: None
        :rtype: None
        '''

        # Update the name; validate_assignment=True handles re-validation.
        self.name = name

    # * method: set_description
    def set_description(self, description: str | None) -> None:
        '''
        Set the category description.

        :param description: The new description, or None to clear.
        :type description: str | None
        :return: None
        :rtype: None
        '''

        # Update the description.
        self.description = description

    # * method: set_icon
    def set_icon(self, icon: str | None) -> None:
        '''
        Set the category icon.

        :param icon: The new icon identifier, or None to clear.
        :type icon: str | None
        :return: None
        :rtype: None
        '''

        # Update the icon.
        self.icon = icon

    # * method: set_color
    def set_color(self, color: str | None) -> None:
        '''
        Set the category color.

        :param color: The new hex color string, or None to clear.
        :type color: str | None
        :return: None
        :rtype: None
        '''

        # Update the color.
        self.color = color


# ** mapper: category_node_object
class CategoryNodeObject(Category, NodeObject):
    '''
    An HDF5 node-attribute representation of a knowledge base category.

    Category metadata is stored as attributes on an HDF5 group node
    at ``/kb/categories/<id>``.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_h5.attrs': {'by_alias': True, 'exclude': {'id'}},
    }

    # * method: map
    def map(self, **overrides) -> CategoryAggregate:
        '''
        Map the node object data to a category aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new category aggregate.
        :rtype: CategoryAggregate
        '''

        # Map to the category aggregate.
        return super().map(CategoryAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, category: Category, **overrides) -> 'CategoryNodeObject':
        '''
        Create a CategoryNodeObject from a Category model.

        :param category: The category model to copy from.
        :type category: Category
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new CategoryNodeObject.
        :rtype: CategoryNodeObject
        '''

        # Create a new CategoryNodeObject from the model.
        return super().from_model(category, **overrides)
