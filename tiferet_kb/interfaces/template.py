"""tiferet_kb Interfaces Template"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List, Optional

# ** app
from tiferet.interfaces import Service

# *** interfaces

# ** interface: template_service
class TemplateService(Service):
    '''
    Service interface for managing knowledge base templates.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if a template exists by ID.

        :param id: The template identifier.
        :type id: str
        :return: True if the template exists, otherwise False.
        :rtype: bool
        '''
        raise NotImplementedError('exists method is required for TemplateService.')

    # * method: get
    @abstractmethod
    def get(self, id: str):
        '''
        Retrieve a template by ID, including its sections.

        :param id: The template identifier.
        :type id: str
        :return: The template aggregate with sections, or None.
        '''
        raise NotImplementedError('get method is required for TemplateService.')

    # * method: list
    @abstractmethod
    def list(self, category_id: Optional[str] = None) -> List:
        '''
        List templates, optionally filtered by category.

        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :return: A list of template aggregates.
        :rtype: List
        '''
        raise NotImplementedError('list method is required for TemplateService.')

    # * method: save
    @abstractmethod
    def save(self, template) -> None:
        '''
        Save or update a template (header only).

        :param template: The template aggregate to save.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('save method is required for TemplateService.')

    # * method: save_section
    @abstractmethod
    def save_section(self, section) -> None:
        '''
        Save or update a template section.

        :param section: The template section aggregate to save.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('save_section method is required for TemplateService.')

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete a template and all its sections by ID. Idempotent.

        :param id: The template identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('delete method is required for TemplateService.')
