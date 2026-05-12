"""tiferet_kb Category Events"""

# *** imports

# ** core
from typing import Any, List

# ** app
from tiferet.events import DomainEvent

from ..assets import constants as const
from ..domain import Category
from ..interfaces import CategoryService
from ..mappers import CategoryAggregate

# *** events

# ** event: add_category
class AddCategory(DomainEvent):
    '''
    Event to create a new knowledge base category.
    '''

    # * attribute: category_service
    category_service: CategoryService

    # * init
    def __init__(self, category_service: CategoryService):
        '''
        Initialize the AddCategory event.

        :param category_service: The category service for persistence.
        :type category_service: CategoryService
        '''

        # Set the category service dependency.
        self.category_service = category_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name'])
    def execute(self,
            id: str,
            name: str,
            description: str | None = None,
            icon: str | None = None,
            color: str | None = None,
            **kwargs,
        ) -> Category:
        '''
        Create a new category.

        :param id: The slug-style category identifier.
        :type id: str
        :param name: The display name for the category.
        :type name: str
        :param description: Optional category description.
        :type description: str | None
        :param icon: Optional icon identifier.
        :type icon: str | None
        :param color: Optional hex color string.
        :type color: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created category.
        :rtype: Category
        '''

        # Create the category aggregate.
        category = CategoryAggregate(
            id=id,
            name=name,
            description=description,
            icon=icon,
            color=color,
        )

        # Verify no duplicate category exists.
        self.verify(
            expression=not self.category_service.exists(category.id),
            error_code=const.KB_CATEGORY_ALREADY_EXISTS_ID,
            message=f'Category with ID {category.id} already exists.',
            id=category.id,
        )

        # Persist the new category.
        self.category_service.save(category)

        # Return the created category.
        return category


# ** event: get_category
class GetCategory(DomainEvent):
    '''
    Event to retrieve a category by its identifier.
    '''

    # * attribute: category_service
    category_service: CategoryService

    # * init
    def __init__(self, category_service: CategoryService):
        '''
        Initialize the GetCategory event.

        :param category_service: The category service for retrieval.
        :type category_service: CategoryService
        '''

        # Set the category service dependency.
        self.category_service = category_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> Category:
        '''
        Retrieve a category by ID.

        :param id: The category identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The retrieved category.
        :rtype: Category
        '''

        # Retrieve the category from the service.
        category = self.category_service.get(id)

        # Verify that the category exists.
        self.verify(
            expression=category is not None,
            error_code=const.KB_CATEGORY_NOT_FOUND_ID,
            category_id=id,
        )

        # Return the retrieved category.
        return category


# ** event: list_categories
class ListCategories(DomainEvent):
    '''
    Event to list all knowledge base categories.
    '''

    # * attribute: category_service
    category_service: CategoryService

    # * init
    def __init__(self, category_service: CategoryService):
        '''
        Initialize the ListCategories event.

        :param category_service: The category service for listing.
        :type category_service: CategoryService
        '''

        # Set the category service dependency.
        self.category_service = category_service

    # * method: execute
    def execute(self, **kwargs) -> List[Category]:
        '''
        List all categories.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A list of categories.
        :rtype: List[Category]
        '''

        # Delegate to the category service.
        return self.category_service.list()


# ** event: update_category
class UpdateCategory(DomainEvent):
    '''
    Event to update an existing category's metadata.

    Supports updating ``name``, ``description``, ``icon``, and ``color``
    attributes via the aggregate mutation methods.
    '''

    # * attribute: category_service
    category_service: CategoryService

    # * init
    def __init__(self, category_service: CategoryService):
        '''
        Initialize the UpdateCategory event.

        :param category_service: The category service for retrieval and persistence.
        :type category_service: CategoryService
        '''

        # Set the category service dependency.
        self.category_service = category_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'attribute'])
    def execute(self,
            id: str,
            attribute: str,
            value: Any = None,
            **kwargs,
        ) -> Category:
        '''
        Update a category attribute.

        :param id: The category identifier.
        :type id: str
        :param attribute: The attribute to update (name, description, icon, color).
        :type attribute: str
        :param value: The new value for the attribute.
        :type value: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The updated category.
        :rtype: Category
        '''

        # Validate that the attribute is supported.
        valid_attributes = {'name', 'description', 'icon', 'color'}
        self.verify(
            expression=attribute in valid_attributes,
            error_code=const.KB_INVALID_CATEGORY_ATTRIBUTE_ID,
            message=f'Invalid category attribute: {attribute}',
            attribute=attribute,
        )

        # When updating the name, ensure a non-empty value is provided.
        if attribute == 'name':
            self.verify(
                expression=isinstance(value, str) and bool(value.strip()),
                error_code=const.KB_INVALID_CATEGORY_ATTRIBUTE_ID,
                message='A category name is required when updating the name attribute.',
            )

        # Retrieve the category from the service.
        category = self.category_service.get(id)

        # Verify that the category exists.
        self.verify(
            expression=category is not None,
            error_code=const.KB_CATEGORY_NOT_FOUND_ID,
            category_id=id,
        )

        # Apply the requested update using aggregate mutation methods.
        if attribute == 'name':
            category.rename(value)
        elif attribute == 'description':
            category.set_description(value)
        elif attribute == 'icon':
            category.set_icon(value)
        elif attribute == 'color':
            category.set_color(value)

        # Persist the updated category.
        self.category_service.save(category)

        # Return the updated category.
        return category


# ** event: remove_category
class RemoveCategory(DomainEvent):
    '''
    Event to remove a category by ID (idempotent).

    Delegates deletion semantics to the underlying ``CategoryService.delete``
    implementation, which is expected to behave idempotently when the
    category does not exist.
    '''

    # * attribute: category_service
    category_service: CategoryService

    # * init
    def __init__(self, category_service: CategoryService):
        '''
        Initialize the RemoveCategory event.

        :param category_service: The category service for deletion.
        :type category_service: CategoryService
        '''

        # Set the category service dependency.
        self.category_service = category_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a category by ID.

        :param id: The category identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The removed category ID.
        :rtype: str
        '''

        # Delete the category (idempotent).
        self.category_service.delete(id)

        # Return the category identifier.
        return id
