"""tiferet_kb Folder H5 Repository"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from tiferet_h5.repos import NodeRepository

from ..interfaces.folder import FolderService
from ..mappers.folder import (
    FolderAggregate,
    FolderNodeObject,
)
from .core import KBNodeRepository

# *** constants

# ** constant: folders_root
FOLDERS_ROOT = '/kb/folders'

# *** repos

# ** repo: folder_h5_repository
class FolderH5Repository(KBNodeRepository, FolderService):
    '''
    HDF5-backed repository for knowledge base folders.

    Folders are stored as node attributes on HDF5 group nodes
    at ``/kb/folders/<id>``.  Each group carries the folder's
    scalar metadata (name, parent_id, path, created_at) as
    attributes via ``FolderNodeObject``.

    ``NodeRepository`` (through ``KBNodeRepository``) owns path resolution, ``save``, and ``exists``.
    ``get`` stays overridden because the identifier is the group name and
    is not an attribute.  ``list`` walks the child groups and filters by
    ``parent_id`` in Python.  ``delete`` removes the group through
    ``KBNodeRepository.remove_node``.
    '''

    # * attribute: node_cls
    node_cls = FolderNodeObject

    # * attribute: node_path
    node_path = f'{FOLDERS_ROOT}/{{id}}'

    # * init
    def __init__(self, h5_file: str, mode: str = 'a') -> None:
        '''
        Initialize the folder H5 repository.

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
        Check if a folder exists by ID.

        :param id: The folder identifier.
        :type id: str
        :return: True if the folder exists, otherwise False.
        :rtype: bool
        '''

        # Delegate to the NodeRepository mixin; a missing file is False.
        return NodeRepository.exists(self, id=id)

    # * method: get
    def get(self, id: str) -> Optional[FolderAggregate]:
        '''
        Retrieve a folder by ID.

        :param id: The folder identifier.
        :type id: str
        :return: The folder aggregate, or None if not found.
        :rtype: FolderAggregate | None
        '''

        # A missing file must not be created by a read.
        if not self.file_exists():
            return None

        group_path = self.resolve_node_path(id=id)

        with self.client() as h5:

            if not h5.node_exists(group_path):
                return None

            attrs = h5.get_node_attrs(group_path)

        return FolderNodeObject.from_attrs(attrs, id=id).map()

    # * method: list
    def list(self, parent_id: Optional[str] = None) -> List[FolderAggregate]:
        '''
        List folders, optionally filtered by parent_id.

        :param parent_id: Optional parent folder ID to filter by.
            Use ``'__root__'`` to list only root-level folders (parent_id is None).
            Use ``None`` (default) to list all folders.
        :type parent_id: str | None
        :return: A list of folder aggregates.
        :rtype: List[FolderAggregate]
        '''

        folders: List[FolderAggregate] = []

        # A missing file yields an empty list and must not be created.
        if not self.file_exists():
            return folders

        with self.client() as h5:

            if not h5.node_exists(FOLDERS_ROOT):
                return folders

            root = h5.get_group(FOLDERS_ROOT)
            for child in root._v_children.values():
                attrs = h5.get_node_attrs(child._v_pathname)
                folder_id = child._v_name
                folder = FolderNodeObject.from_attrs(attrs, id=folder_id).map()

                # Filter by parent_id if specified.
                if parent_id == '__root__':
                    if folder.parent_id is not None:
                        continue
                elif parent_id is not None:
                    if folder.parent_id != parent_id:
                        continue

                folders.append(folder)

        return folders

    # * method: save
    def save(self, folder: FolderAggregate) -> None:
        '''
        Save or update a folder.

        :param folder: The folder aggregate to save.
        :type folder: FolderAggregate
        :return: None
        :rtype: None
        '''

        # Convert the aggregate to a node object and delegate to the mixin,
        # which creates the group when absent and writes the attributes.
        node_obj = FolderNodeObject.from_model(folder)
        NodeRepository.save(self, node_obj, id=folder.id)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete a folder by ID. Idempotent.

        :param id: The folder identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # A missing file has nothing to delete and must not be created.
        if not self.file_exists():
            return

        group_path = self.resolve_node_path(id=id)

        with self.client() as h5:

            # Remove the group and its contents; a missing node is a no-op.
            self.remove_node(h5, group_path, recursive=True)

    # * method: move
    def move(self, id: str, new_parent_id: Optional[str] = None) -> None:
        '''
        Move a folder to a new parent by updating its parent_id attribute.

        :param id: The folder identifier to move.
        :type id: str
        :param new_parent_id: The new parent folder ID, or None for root.
        :type new_parent_id: str | None
        :return: None
        :rtype: None
        '''

        # A missing file has nothing to move and must not be created.
        if not self.file_exists():
            return

        group_path = self.resolve_node_path(id=id)

        with self.client() as h5:

            if not h5.node_exists(group_path):
                return

            # Update the parent_id attribute.
            h5.set_node_attr(group_path, 'parent_id', new_parent_id or '')
