"""tiferet_kb Interfaces Folder"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List, Optional

# ** app
from tiferet.interfaces import Service

# *** interfaces

# ** interface: folder_service
class FolderService(Service):
    '''
    Service interface for managing knowledge base folders.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if a folder exists by ID.

        :param id: The folder identifier.
        :type id: str
        :return: True if the folder exists, otherwise False.
        :rtype: bool
        '''
        raise NotImplementedError('exists method is required for FolderService.')

    # * method: get
    @abstractmethod
    def get(self, id: str):
        '''
        Retrieve a folder by ID.

        :param id: The folder identifier.
        :type id: str
        :return: The folder aggregate, or None if not found.
        '''
        raise NotImplementedError('get method is required for FolderService.')

    # * method: list
    @abstractmethod
    def list(self, parent_id: Optional[str] = None) -> List:
        '''
        List folders, optionally filtered by parent.

        :param parent_id: Optional parent folder ID. None returns root-level folders.
        :type parent_id: str | None
        :return: A list of folder aggregates.
        :rtype: List
        '''
        raise NotImplementedError('list method is required for FolderService.')

    # * method: save
    @abstractmethod
    def save(self, folder) -> None:
        '''
        Save or update a folder.

        :param folder: The folder aggregate to save.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('save method is required for FolderService.')

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete a folder by ID. Idempotent.

        :param id: The folder identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('delete method is required for FolderService.')

    # * method: move
    @abstractmethod
    def move(self, id: str, new_parent_id: Optional[str] = None) -> None:
        '''
        Move a folder to a new parent (or to root if new_parent_id is None).

        :param id: The folder identifier to move.
        :type id: str
        :param new_parent_id: The new parent folder ID, or None for root.
        :type new_parent_id: str | None
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('move method is required for FolderService.')
