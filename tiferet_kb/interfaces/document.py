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

    # * method: embed_section
    @abstractmethod
    def embed_section(self,
            section_id: str,
            embedding: List[float],
            model_name: str,
        ) -> None:
        '''
        Store or replace an embedding vector for a document section.

        :param section_id: The section identifier.
        :type section_id: str
        :param embedding: The embedding vector as a list of floats.
        :type embedding: List[float]
        :param model_name: The name of the embedding model.
        :type model_name: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('embed_section method is required for DocumentService.')

    # * method: search_similar
    @abstractmethod
    def search_similar(self,
            query_embedding: List[float],
            limit: int = 5,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
        ) -> List:
        '''
        Search for document sections similar to the query embedding using cosine similarity.

        :param query_embedding: The query embedding vector.
        :type query_embedding: List[float]
        :param limit: Maximum number of results to return.
        :type limit: int
        :param folder_id: Optional folder identifier to filter by.
        :type folder_id: str | None
        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :return: A list of dicts with section_id and similarity score.
        :rtype: List
        '''
        raise NotImplementedError('search_similar method is required for DocumentService.')

    # * method: get_embedding
    @abstractmethod
    def get_embedding(self, section_id: str) -> Optional[List[float]]:
        '''
        Retrieve the stored embedding for a section, or None if not embedded.

        :param section_id: The section identifier.
        :type section_id: str
        :return: The embedding vector, or None.
        :rtype: List[float] | None
        '''
        raise NotImplementedError('get_embedding method is required for DocumentService.')

    # * method: remove_embedding
    @abstractmethod
    def remove_embedding(self, section_id: str) -> None:
        '''
        Remove the embedding for a section without deleting the section itself.

        :param section_id: The section identifier.
        :type section_id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('remove_embedding method is required for DocumentService.')
