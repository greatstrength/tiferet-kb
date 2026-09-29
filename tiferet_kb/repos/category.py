"""tiferet_kb Category H5 Repository"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from tiferet_h5.repos import H5Repository, NodeRepository

from ..interfaces import CategoryService
from ..mappers import (
    CategoryAggregate,
    CategoryNodeObject,
)
from ..utils.h5 import remove_node

# *** constants

# ** constant: categories_root
CATEGORIES_ROOT = '/kb/categories'

# *** repos

# ** repo: category_h5_repository
class CategoryH5Repository(NodeRepository, H5Repository, CategoryService):
    '''
    HDF5-backed repository for knowledge base categories.

    Categories are stored as node attributes on HDF5 group nodes
    at ``/kb/categories/<id>``.  Each group carries the category's
    scalar metadata (name, description, icon, color) as attributes
    via ``CategoryNodeObject``.

    ``NodeRepository`` owns path resolution, ``save``, and ``exists``.
    ``get`` stays overridden because the identifier is the group name and
    is not an attribute.  ``list`` walks the child groups.  ``delete``
    removes the group through ``tiferet_kb.utils.h5.remove_node``.
    '''

    # * attribute: node_cls
    node_cls = CategoryNodeObject

    # * attribute: node_path
    node_path = f'{CATEGORIES_ROOT}/{{id}}'

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

        # Delegate to the NodeRepository mixin; a missing file is False.
        return NodeRepository.exists(self, id=id)

    # * method: get
    def get(self, id: str) -> Optional[CategoryAggregate]:
        '''
        Retrieve a category by ID.

        :param id: The category identifier.
        :type id: str
        :return: The category aggregate, or None if not found.
        :rtype: CategoryAggregate | None
        '''

        # A missing file must not be created by a read.
        if not self.file_exists():
            return None

        # Resolve the HDF5 group path for the category.
        group_path = self.resolve_node_path(id=id)

        # Read attributes from the group node.
        with self.client() as h5:

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

        # A missing file yields an empty list and must not be created.
        if not self.file_exists():
            return categories

        with self.client() as h5:

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

        # Convert the aggregate to a node object and delegate to the mixin,
        # which creates the group when absent and writes the attributes.
        node_obj = CategoryNodeObject.from_model(category)
        NodeRepository.save(self, node_obj, id=category.id)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete a category by ID. This operation is idempotent.

        :param id: The category identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # A missing file has nothing to delete and must not be created.
        if not self.file_exists():
            return

        # Resolve the HDF5 group path for the category.
        group_path = self.resolve_node_path(id=id)

        with self.client() as h5:

            # Remove the group and its contents; a missing node is a no-op.
            remove_node(h5, group_path, recursive=True)
