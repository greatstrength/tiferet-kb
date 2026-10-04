"""tiferet_kb Interfaces Document"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any, Dict, List, Optional

# ** app
from tiferet.interfaces import Service

from ..mappers.comment import SectionCommentAggregate

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
            title: Optional[str] = None,
            include_sections: bool = False,
            include_properties: bool = False,
            property_name: Optional[str] = None,
            property_value: Any = None,
            property_value_type: Optional[str] = None,
            visibility: Optional[str] = None,
            owner_id: Optional[str] = None,
        ) -> List:
        '''
        List documents with optional filters.

        Property arguments are additive. Omitting all three adds no property
        condition. ``False``, ``0``, and ``''`` are real filter values.

        :param folder_id: Optional folder identifier to filter by.
        :type folder_id: str | None
        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :param status: Optional status to filter by (draft, published, archived).
        :type status: str | None
        :param title: Optional exact document title. Empty or omitted adds no condition.
        :type title: str | None
        :param include_sections: If True, populate sections for each document.
        :type include_sections: bool
        :param include_properties: If True, populate each document's property bag.
        :type include_properties: bool
        :param property_name: Optional property name to match exactly.
        :type property_name: str | None
        :param property_value: Optional property value to match exactly.
        :type property_value: Any
        :param property_value_type: Optional declared type of the property value.
        :type property_value_type: str | None
        :param visibility: Optional visibility to filter by. ``public`` includes
            stored public, empty, and absent. Omitted does not constrain the field.
        :type visibility: str | None
        :param owner_id: Optional owner identifier to filter by. An absent owner
            matches no owner filter. Omitted does not constrain the field.
        :type owner_id: str | None
        :return: A list of document aggregates.
        :rtype: List
        '''
        raise NotImplementedError('list method is required for DocumentService.')

    # * method: set_property
    @abstractmethod
    def set_property(self,
            document_id: str,
            name: str,
            value: Any,
            value_type: str,
        ):
        '''
        Set one named typed value on an existing document, replacing that name.

        :param document_id: The document identifier.
        :type document_id: str
        :param name: The property name.
        :type name: str
        :param value: The property value.
        :type value: Any
        :param value_type: The declared type: string, number, or boolean.
        :type value_type: str
        :return: The stored property.
        '''
        raise NotImplementedError('set_property method is required for DocumentService.')

    # * method: remove_property
    @abstractmethod
    def remove_property(self, document_id: str, name: str) -> bool:
        '''
        Remove one property by name. Absent rows succeed.

        :param document_id: The document identifier.
        :type document_id: str
        :param name: The property name.
        :type name: str
        :return: True when a row was removed.
        :rtype: bool
        '''
        raise NotImplementedError('remove_property method is required for DocumentService.')

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
            document_id: Optional[str] = None,
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
        :param document_id: Optional document identifier. Omitted means file-wide.
        :type document_id: str | None
        :return: A list of dicts with section_id and similarity score.
        :rtype: List
        '''
        raise NotImplementedError('search_similar method is required for DocumentService.')

    # * method: search_keyword
    @abstractmethod
    def search_keyword(self,
            query: str,
            limit: int = 5,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
            document_id: Optional[str] = None,
        ) -> List[Dict]:
        '''
        Search sections by the words in their rendered bodies.

        :param query: The query string.
        :type query: str
        :param limit: Maximum number of results to return, after filters.
        :type limit: int
        :param folder_id: Optional folder identifier to filter by.
        :type folder_id: str | None
        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :param document_id: Optional document identifier. Omitted means file-wide.
        :type document_id: str | None
        :return: A list of dicts with section_id and BM25 score.
        :rtype: List[Dict]
        '''
        raise NotImplementedError('search_keyword method is required for DocumentService.')

    # * method: search_composed
    @abstractmethod
    def search_composed(self,
            query: str,
            query_embedding: List[float],
            limit: int = 5,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
            document_id: Optional[str] = None,
        ) -> List[Dict]:
        '''
        Merge keyword rank and embedding rank for one query.

        The caller supplies the query vector. This method does not compute it.

        :param query: The query string.
        :type query: str
        :param query_embedding: The caller-supplied query vector.
        :type query_embedding: List[float]
        :param limit: Maximum number of results to return, after fusion.
        :type limit: int
        :param folder_id: Optional folder identifier to filter by.
        :type folder_id: str | None
        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :param document_id: Optional document identifier. Omitted means file-wide.
        :type document_id: str | None
        :return: A list of dicts with section_id and fusion score.
        :rtype: List[Dict]
        '''
        raise NotImplementedError('search_composed method is required for DocumentService.')

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

    # * method: add_comment
    @abstractmethod
    def add_comment(self, comment: SectionCommentAggregate) -> bool:
        '''
        Insert a section comment. Does not replace an existing id.

        :param comment: The comment aggregate to insert.
        :type comment: SectionCommentAggregate
        :return: True if the row was inserted, False if the id already exists and nothing was written.
        :rtype: bool
        '''
        raise NotImplementedError('add_comment method is required for DocumentService.')

    # * method: list_comments
    @abstractmethod
    def list_comments(self, section_id: str) -> List[SectionCommentAggregate]:
        '''
        List comments on a section, ordered by stored created_at then id.

        A missing table is an empty list. This method does not check that the section exists.

        :param section_id: The section identifier.
        :type section_id: str
        :return: A flat list of comment aggregates. Each item carries its own parent id.
        :rtype: List[SectionCommentAggregate]
        '''
        raise NotImplementedError('list_comments method is required for DocumentService.')

    # * method: delete_comment
    @abstractmethod
    def delete_comment(self, id: str) -> Optional[bool]:
        '''
        Delete one comment when nothing replies to it.

        :param id: The comment identifier.
        :type id: str
        :return: True if the row was deleted, None if the id is not stored,
            False if a reply still names it and nothing was deleted.
        :rtype: bool | None
        '''
        raise NotImplementedError('delete_comment method is required for DocumentService.')

    # * method: add_link
    @abstractmethod
    def add_link(self, link):
        '''
        Store one directional document link.

        Refuses the write when the id is already a link id, or when the
        source, target, and type are already stored. Does not insert and
        then roll back. Does not write the reverse row.

        :param link: The document link aggregate to store.
        :return: The stored link.
        '''
        raise NotImplementedError('add_link method is required for DocumentService.')

    # * method: list_links
    @abstractmethod
    def list_links(self,
            document_id: str,
            direction: str = 'both',
            link_type: Optional[str] = None,
        ) -> List:
        '''
        List links for one document.

        A missing link table is an empty list and is not created. ``outgoing``
        keeps rows whose source is the document. ``incoming`` keeps rows whose
        target is the document. ``both`` returns outgoing rows, then incoming rows.

        :param document_id: The document whose links are listed.
        :type document_id: str
        :param direction: ``outgoing``, ``incoming``, or ``both``.
        :type direction: str
        :param link_type: Optional exact type filter. Omitted means every type.
        :type link_type: str | None
        :return: The matching links.
        :rtype: List
        '''
        raise NotImplementedError('list_links method is required for DocumentService.')

    # * method: remove_link
    @abstractmethod
    def remove_link(self, id: str) -> None:
        '''
        Remove one link row by id. This operation is idempotent.

        Deleting the last row does not delete the link table. A missing
        table is not an error.

        :param id: The link identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('remove_link method is required for DocumentService.')
