"""tiferet_kb Folder Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** app
from tiferet.mappers import Aggregate
from tiferet_h5.mappers import NodeObject

from ..domain.folder import Folder

# *** mappers

# ** mapper: folder_aggregate
class FolderAggregate(Folder, Aggregate):
    '''
    A mutable aggregate representation of a knowledge base folder.
    '''

    # * method: rename
    def rename(self, name: str) -> None:
        '''
        Rename the folder.

        :param name: The new folder name.
        :type name: str
        :return: None
        :rtype: None
        '''

        # Update the name.
        self.name = name

    # * method: set_parent
    def set_parent(self, parent_id: str | None) -> None:
        '''
        Set the parent folder.

        :param parent_id: The new parent folder ID, or None for root.
        :type parent_id: str | None
        :return: None
        :rtype: None
        '''

        # Update the parent_id.
        self.parent_id = parent_id

    # * method: update_path
    def update_path(self, path: str) -> None:
        '''
        Update the materialized path.

        :param path: The new path string.
        :type path: str
        :return: None
        :rtype: None
        '''

        # Update the path.
        self.path = path


# ** mapper: folder_node_object
class FolderNodeObject(Folder, NodeObject):
    '''
    An HDF5 node-attribute representation of a knowledge base folder.

    Folder metadata is stored as attributes on an HDF5 group node
    at ``/kb/folders/<id>``.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_h5.attrs': {'by_alias': True, 'exclude': {'id'}},
    }

    # * method: map
    def map(self, **overrides) -> FolderAggregate:
        '''
        Map the node object data to a folder aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new folder aggregate.
        :rtype: FolderAggregate
        '''

        # Map to the folder aggregate.
        return super().map(FolderAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, folder: Folder, **overrides) -> 'FolderNodeObject':
        '''
        Create a FolderNodeObject from a Folder model.

        :param folder: The folder model to copy from.
        :type folder: Folder
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new FolderNodeObject.
        :rtype: FolderNodeObject
        '''

        # Create a new FolderNodeObject from the model.
        return super().from_model(folder, **overrides)
