"""tiferet_kb Interfaces Category"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List, Optional

# ** app
from tiferet.interfaces import Service

# *** interfaces

# ** interface: category_service
class CategoryService(Service):
    '''
    Service interface for managing knowledge base categories.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if a category exists by ID.

        :param id: The category identifier.
        :type id: str
        :return: True if the category exists, otherwise False.
        :rtype: bool
        '''
        raise NotImplementedError('exists method is required for CategoryService.')

    # * method: get
    @abstractmethod
    def get(self, id: str):
        '''
        Retrieve a category by ID.

        :param id: The category identifier.
        :type id: str
        :return: The category aggregate, or None if not found.
        '''
        raise NotImplementedError('get method is required for CategoryService.')

    # * method: list
    @abstractmethod
    def list(self) -> List:
        '''
        List all categories.

        :return: A list of category aggregates.
        :rtype: List
        '''
        raise NotImplementedError('list method is required for CategoryService.')

    # * method: save
    @abstractmethod
    def save(self, category) -> None:
        '''
        Save or update a category.

        :param category: The category aggregate to save.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('save method is required for CategoryService.')

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete a category by ID. This operation should be idempotent.

        :param id: The category identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('delete method is required for CategoryService.')
