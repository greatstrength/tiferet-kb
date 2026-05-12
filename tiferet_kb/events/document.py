"""tiferet_kb Document Events"""

# *** imports

# ** core
from typing import Any, List

# ** app
from tiferet.events import DomainEvent

from ..assets import constants as const
from ..domain.document import Document
from ..interfaces.document import DocumentService
from ..mappers.document import DocumentAggregate

# *** events

# ** event: add_document
class AddDocument(DomainEvent):
    '''
    Event to create a new knowledge base document.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the AddDocument event.

        :param document_service: The document service for persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['title'])
    def execute(self,
            title: str,
            id: str | None = None,
            category_id: str | None = None,
            template_id: str | None = None,
            folder_id: str | None = None,
            status: str | None = None,
            **kwargs,
        ) -> Document:
        '''
        Create a new document.

        :param title: The document title.
        :type title: str
        :param id: Optional explicit UUID.
        :type id: str | None
        :param category_id: Optional category identifier.
        :type category_id: str | None
        :param template_id: Optional template identifier.
        :type template_id: str | None
        :param folder_id: Optional folder identifier.
        :type folder_id: str | None
        :param status: Optional initial status (defaults to 'draft').
        :type status: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created document.
        :rtype: Document
        '''

        # Build the aggregate construction kwargs.
        doc_kwargs = dict(title=title)
        if id:
            doc_kwargs['id'] = id
        if category_id:
            doc_kwargs['category_id'] = category_id
        if template_id:
            doc_kwargs['template_id'] = template_id
        if folder_id:
            doc_kwargs['folder_id'] = folder_id
        if status:
            doc_kwargs['status'] = status

        # Create the document aggregate (UUID and timestamps auto-derived).
        document = DocumentAggregate(**doc_kwargs)

        # Verify no duplicate document exists.
        self.verify(
            expression=not self.document_service.exists(document.id),
            error_code=const.KB_DOCUMENT_ALREADY_EXISTS_ID,
            message=f'Document with ID {document.id} already exists.',
            id=document.id,
        )

        # Validate status if provided.
        if status:
            valid_statuses = {'draft', 'published', 'archived'}
            self.verify(
                expression=status in valid_statuses,
                error_code=const.KB_INVALID_DOCUMENT_STATUS_ID,
                message=f'Invalid document status: {status}',
                status=status,
            )

        # Persist the new document.
        self.document_service.save(document)

        # Return the created document.
        return document


# ** event: get_document
class GetDocument(DomainEvent):
    '''
    Event to retrieve a document by its identifier, including sections.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the GetDocument event.

        :param document_service: The document service for retrieval.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> Document:
        '''
        Retrieve a document by ID.

        :param id: The document identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The retrieved document with sections.
        :rtype: Document
        '''

        # Retrieve the document from the service.
        document = self.document_service.get(id)

        # Verify that the document exists.
        self.verify(
            expression=document is not None,
            error_code=const.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=id,
        )

        # Return the retrieved document.
        return document


# ** event: list_documents
class ListDocuments(DomainEvent):
    '''
    Event to list documents with optional filters.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the ListDocuments event.

        :param document_service: The document service for listing.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    def execute(self,
            folder_id: str | None = None,
            category_id: str | None = None,
            status: str | None = None,
            **kwargs,
        ) -> List[Document]:
        '''
        List documents with optional filters.

        :param folder_id: Optional folder identifier to filter by.
        :type folder_id: str | None
        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :param status: Optional status to filter by.
        :type status: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A list of documents.
        :rtype: List[Document]
        '''

        # Delegate to the document service.
        return self.document_service.list(
            folder_id=folder_id,
            category_id=category_id,
            status=status,
        )


# ** event: update_document
class UpdateDocument(DomainEvent):
    '''
    Event to update an existing document's metadata.

    Supports updating ``title``, ``status``, ``category_id``, and ``folder_id``.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the UpdateDocument event.

        :param document_service: The document service for retrieval and persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'attribute'])
    def execute(self,
            id: str,
            attribute: str,
            value: Any = None,
            **kwargs,
        ) -> Document:
        '''
        Update a document attribute.

        :param id: The document identifier.
        :type id: str
        :param attribute: The attribute to update.
        :type attribute: str
        :param value: The new value for the attribute.
        :type value: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The updated document.
        :rtype: Document
        '''

        # Validate that the attribute is supported.
        valid_attributes = {'title', 'status', 'category_id', 'folder_id'}
        self.verify(
            expression=attribute in valid_attributes,
            error_code=const.KB_INVALID_DOCUMENT_ATTRIBUTE_ID,
            message=f'Invalid document attribute: {attribute}',
            attribute=attribute,
        )

        # Validate status values.
        if attribute == 'status':
            valid_statuses = {'draft', 'published', 'archived'}
            self.verify(
                expression=value in valid_statuses,
                error_code=const.KB_INVALID_DOCUMENT_STATUS_ID,
                message=f'Invalid document status: {value}',
                status=value,
            )

        # When updating the title, ensure a non-empty value.
        if attribute == 'title':
            self.verify(
                expression=isinstance(value, str) and bool(value.strip()),
                error_code=const.KB_INVALID_DOCUMENT_ATTRIBUTE_ID,
                message='A document title is required.',
            )

        # Retrieve the document from the service.
        document = self.document_service.get(id)

        # Verify that the document exists.
        self.verify(
            expression=document is not None,
            error_code=const.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=id,
        )

        # Apply the requested update using aggregate mutation methods.
        if attribute == 'title':
            document.rename(value)
        elif attribute == 'status':
            document.set_status(value)
        elif attribute == 'category_id':
            document.set_category(value)
        elif attribute == 'folder_id':
            document.set_folder(value)

        # Persist the updated document.
        self.document_service.save(document)

        # Return the updated document.
        return document


# ** event: remove_document
class RemoveDocument(DomainEvent):
    '''
    Event to remove a document by ID (idempotent, cascading sections).
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the RemoveDocument event.

        :param document_service: The document service for deletion.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a document and all its sections by ID.

        :param id: The document identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The removed document ID.
        :rtype: str
        '''

        # Delete the document (cascades to sections, idempotent).
        self.document_service.delete(id)

        # Return the document identifier.
        return id
