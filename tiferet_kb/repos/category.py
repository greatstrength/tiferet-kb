"""tiferet_kb Category H5 Repository"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from tiferet_h5.repos import H5Repository

from ..interfaces import CategoryService
from ..mappers import (
    CategoryAggregate,
    CategoryNodeObject,
)

# *** constants

# ** constant: categories_root
CATEGORIES_ROOT = '/kb/categories'

# *** repos

# ** repo: category_h5_repository
class CategoryH5Repository(H5Repository, CategoryService):
    '''
    HDF5-backed repository for knowledge base categories.

    Categories are stored as node attributes on HDF5 group nodes
    at ``/kb/categories/<id>``.  Each group carries the category's
    scalar metadata (name, description, icon, color) as attributes
    via ``CategoryNodeObject``.
    '''

    # * init
    def __init__(self, h5_file: str, mode: str = 'a') -> None:
        '''
        Initialize the category H5 repository.

        :param h5_file: Path to the HDF5 file.
        :type h5_file: str
        :param mode: Default PyTables open mode.
        :type mode: str
        '''

        # Initialize the parent H5Repository.
        super().__init__(h5_file=h5_file, mode=mode)

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a category exists by ID.

        :param id: The category identifier.
        :type id: str
        :return: True if the category exists, otherwise False.
        :rtype: bool
        '''

        # Build the HDF5 group path for the category.
        group_path = f'{CATEGORIES_ROOT}/{id}'

        # Check node existence within a context-managed client.
        with self.client(mode='r') as h5:
            return h5.node_exists(group_path)

    # * method: get
    def get(self, id: str) -> Optional[CategoryAggregate]:
        '''
        Retrieve a category by ID.

        :param id: The category identifier.
        :type id: str
        :return: The category aggregate, or None if not found.
        :rtype: CategoryAggregate | None
        '''

        # Build the HDF5 group path for the category.
        group_path = f'{CATEGORIES_ROOT}/{id}'

        # Read attributes from the group node.
        with self.client(mode='r') as h5:

            # Return None if the group does not exist.
            if not h5.node_exists(group_path):
                return None

            # Load the node attributes.
            attrs = h5.get_node_attrs(group_path)

        # Map the attributes to a category aggregate, injecting the id.
        return CategoryNodeObject.from_attrs(attrs, id=id).map()

    # * method: list
    def list(self) -> List[CategoryAggregate]:
        '''
        List all categories.

        :return: A list of category aggregates.
        :rtype: List[CategoryAggregate]
        '''

        # Collect all category aggregates.
        categories: List[CategoryAggregate] = []

        with self.client(mode='r') as h5:

            # Return empty if the root group does not exist.
            if not h5.node_exists(CATEGORIES_ROOT):
                return categories

            # Iterate over child groups under the categories root.
            root = h5.get_group(CATEGORIES_ROOT)
            for child in root._v_children.values():

                # Read attributes from each child group.
                attrs = h5.get_node_attrs(child._v_pathname)
                category_id = child._v_name

                # Map to aggregate and collect.
                categories.append(
                    CategoryNodeObject.from_attrs(attrs, id=category_id).map()
                )

        # Return the collected categories.
        return categories

    # * method: save
    def save(self, category: CategoryAggregate) -> None:
        '''
        Save or update a category.

        :param category: The category aggregate to save.
        :type category: CategoryAggregate
        :return: None
        :rtype: None
        '''

        # Build the HDF5 group path for the category.
        group_path = f'{CATEGORIES_ROOT}/{category.id}'

        # Convert the aggregate to a node object for attribute serialization.
        node_obj = CategoryNodeObject.from_model(category)
        attr_data = node_obj.to_attrs()

        with self.client() as h5:

            # Create the group if it does not already exist.
            if not h5.node_exists(group_path):

                # Ensure the categories root exists.
                if not h5.node_exists(CATEGORIES_ROOT):
                    h5.create_group(CATEGORIES_ROOT, title='Knowledge Base Categories')

                # Create the category group.
                h5.create_group(group_path, title=category.name)

            # Write each attribute to the group node.
            for attr_name, attr_value in attr_data.items():
                h5.set_node_attr(group_path, attr_name, attr_value)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete a category by ID. This operation is idempotent.

        :param id: The category identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # Build the HDF5 group path for the category.
        group_path = f'{CATEGORIES_ROOT}/{id}'

        with self.client() as h5:

            # Skip silently if the group does not exist (idempotent).
            if not h5.node_exists(group_path):
                return

            # Remove the group node and all its contents.
            h5.h5file.remove_node(group_path, recursive=True)
