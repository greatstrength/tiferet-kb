"""tiferet_kb Interfaces Document"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List, Optional

# ** app
from tiferet.interfaces import Service

# *** interfaces

# ** interface: document_service
class DocumentService(Service):
    '''
    Service interface for managing knowledge base documents and their sections.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if a document exists by ID.

        :param id: The document identifier.
        :type id: str
        :return: True if the document exists, otherwise False.
        :rtype: bool
        '''
        raise NotImplementedError('exists method is required for DocumentService.')

    # * method: get
    @abstractmethod
    def get(self, id: str):
        '''
        Retrieve a document by ID, including its sections.

        :param id: The document identifier.
        :type id: str
        :return: The document aggregate with sections populated, or None.
        '''
        raise NotImplementedError('get method is required for DocumentService.')

    # * method: list
    @abstractmethod
    def list(self,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
            status: Optional[str] = None,
        ) -> List:
        '''
        List documents with optional filters.

        :param folder_id: Optional folder identifier to filter by.
        :type folder_id: str | None
        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :param status: Optional status to filter by (draft, published, archived).
        :type status: str | None
        :return: A list of document aggregates.
        :rtype: List
        '''
        raise NotImplementedError('list method is required for DocumentService.')

    # * method: save
    @abstractmethod
    def save(self, document) -> None:
        '''
        Save or update a document (header only, without sections).

        :param document: The document aggregate to save.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('save method is required for DocumentService.')

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete a document and all its sections by ID. This operation should be idempotent.

        :param id: The document identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('delete method is required for DocumentService.')

    # * method: get_sections
    @abstractmethod
    def get_sections(self, document_id: str) -> List:
        '''
        Retrieve all sections for a document, ordered by position.

        :param document_id: The parent document identifier.
        :type document_id: str
        :return: A list of document section aggregates.
        :rtype: List
        '''
        raise NotImplementedError('get_sections method is required for DocumentService.')

    # * method: save_section
    @abstractmethod
    def save_section(self, section) -> None:
        '''
        Save or update a document section.

        :param section: The document section aggregate to save.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('save_section method is required for DocumentService.')

    # * method: delete_section
    @abstractmethod
    def delete_section(self, section_id: str) -> None:
        '''
        Delete a document section by ID. This operation should be idempotent.

        :param section_id: The section identifier.
        :type section_id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('delete_section method is required for DocumentService.')

    # * method: reorder_sections
    @abstractmethod
    def reorder_sections(self, document_id: str, section_ids: List[str]) -> None:
        '''
        Reorder sections within a document by providing the desired ordering of section IDs.

        :param document_id: The parent document identifier.
        :type document_id: str
        :param section_ids: The section IDs in the desired order.
        :type section_ids: List[str]
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('reorder_sections method is required for DocumentService.')
