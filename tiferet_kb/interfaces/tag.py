"""tiferet_kb Interfaces Tag"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from tiferet.interfaces import Service

# *** interfaces

# ** interface: tag_service
class TagService(Service):
    '''
    Service interface for tag labels and the document–tag association.

    The label catalog and the association live here, not on the document
    header. Events compose document existence checks with these operations.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if a tag exists by ID.

        :param id: The tag identifier.
        :type id: str
        :return: True if the tag exists, otherwise False.
        :rtype: bool
        '''
        raise NotImplementedError('exists method is required for TagService.')

    # * method: get
    @abstractmethod
    def get(self, id: str):
        '''
        Retrieve a tag by ID.

        :param id: The tag identifier.
        :type id: str
        :return: The tag aggregate, or None if not found.
        '''
        raise NotImplementedError('get method is required for TagService.')

    # * method: list
    @abstractmethod
    def list(self) -> List:
        '''
        List all tags.

        :return: A list of tag aggregates.
        :rtype: List
        '''
        raise NotImplementedError('list method is required for TagService.')

    # * method: save
    @abstractmethod
    def save(self, tag) -> None:
        '''
        Save or update a tag.

        :param tag: The tag aggregate to save.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('save method is required for TagService.')

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete a tag label by ID. This operation should be idempotent.

        Does not clear associations. The caller checks carriers first.

        :param id: The tag identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('delete method is required for TagService.')

    # * method: tag_document
    @abstractmethod
    def tag_document(self, document_id: str, tag_id: str) -> None:
        '''
        Record one document–tag association. Repeating it is a no-op.

        :param document_id: The document identifier.
        :type document_id: str
        :param tag_id: The tag identifier.
        :type tag_id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('tag_document method is required for TagService.')

    # * method: untag_document
    @abstractmethod
    def untag_document(self, document_id: str, tag_id: str) -> None:
        '''
        Remove one document–tag association if it is present.

        Absent associations succeed. The tag label is not deleted.

        :param document_id: The document identifier.
        :type document_id: str
        :param tag_id: The tag identifier.
        :type tag_id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('untag_document method is required for TagService.')

    # * method: list_document_ids
    @abstractmethod
    def list_document_ids(self, tag_id: str) -> List[str]:
        '''
        List document identifiers that carry a tag.

        :param tag_id: The tag identifier.
        :type tag_id: str
        :return: Carrier document identifiers, without duplicates.
        :rtype: List[str]
        '''
        raise NotImplementedError('list_document_ids method is required for TagService.')

    # * method: list_tags_for_document
    @abstractmethod
    def list_tags_for_document(self, document_id: str) -> List:
        '''
        List the tags a document carries.

        :param document_id: The document identifier.
        :type document_id: str
        :return: Tag aggregates the document carries. Empty when it carries none.
        :rtype: List
        '''
        raise NotImplementedError('list_tags_for_document method is required for TagService.')

    # * method: clear_document
    @abstractmethod
    def clear_document(self, document_id: str) -> None:
        '''
        Remove every association for a document. Idempotent when none exist.

        :param document_id: The document identifier.
        :type document_id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('clear_document method is required for TagService.')
