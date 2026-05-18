"""tiferet_kb Document Events"""

# *** imports

# ** core
from typing import Any, List

# ** app
from tiferet.events import DomainEvent

from ..assets import constants as const
from ..domain.document import Document, DocumentSection
from ..interfaces.document import DocumentService
from ..mappers.document import DocumentAggregate, DocumentSectionAggregate
from ..utils.markdown import parse_content_to_paragraphs

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


# ** event: add_document_section
class AddDocumentSection(DomainEvent):
    '''
    Event to add a section to an existing document.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the AddDocumentSection event.

        :param document_service: The document service for persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['document_id', 'title'])
    def execute(self,
            document_id: str,
            title: str,
            content: str = '',
            content_type: str = 'markdown',
            heading_level: int = 2,
            icon: str | None = None,
            position: int | None = None,
            **kwargs,
        ) -> DocumentSection:
        '''
        Add a new section to a document.

        Accepts markdown content which is parsed into paragraphs and
        text segments with formatting metadata. The returned section
        carries structured rich-text data for UI rendering.

        :param document_id: The parent document identifier.
        :type document_id: str
        :param title: The section heading.
        :type title: str
        :param content: The markdown content to parse into paragraphs/segments.
        :type content: str
        :param content_type: The section rendering mode (markdown, text, code).
        :type content_type: str
        :param heading_level: The heading level (1-6).
        :type heading_level: int
        :param icon: Optional icon identifier.
        :type icon: str | None
        :param position: Optional position; defaults to appending at the end.
        :type position: int | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created section with structured paragraphs/segments.
        :rtype: DocumentSection
        '''

        # Validate content type.
        valid_types = {'text', 'markdown', 'code'}
        self.verify(
            expression=content_type in valid_types,
            error_code=const.KB_INVALID_CONTENT_TYPE_ID,
            message=f'Invalid content type: {content_type}',
            content_type=content_type,
        )

        # Verify the parent document exists.
        self.verify(
            expression=self.document_service.exists(document_id),
            error_code=const.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=document_id,
        )

        # Determine position: append to end if not specified.
        if position is None:
            existing = self.document_service.get_sections(document_id)
            position = len(existing)

        # Create the section aggregate (UUID auto-generated).
        section = DocumentSectionAggregate(
            document_id=document_id,
            title=title,
            content_type=content_type,
            heading_level=heading_level,
            icon=icon,
            position=position,
        )

        # Parse markdown content into paragraphs with segments.
        if content:
            paragraphs = parse_content_to_paragraphs(content, section.id)
            section.set_paragraphs(paragraphs)

        # Persist the new section.
        self.document_service.save_section(section)

        # Return the created section.
        return section


# ** event: update_document_section
class UpdateDocumentSection(DomainEvent):
    '''
    Event to update a document section's content or metadata.

    Supports updating ``title``, ``content``, and ``content_type``.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the UpdateDocumentSection event.

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
        ) -> DocumentSection:
        '''
        Update a section attribute.

        Supports updating ``title``, ``content`` (re-parsed into paragraphs/segments),
        ``content_type``, ``heading_level``, and ``icon``.

        :param id: The section identifier.
        :type id: str
        :param attribute: The attribute to update.
        :type attribute: str
        :param value: The new value.
        :type value: Any
        :param kwargs: Additional keyword arguments (must include ``document_id``).
        :type kwargs: dict
        :return: The updated section.
        :rtype: DocumentSection
        '''

        # Validate that the attribute is supported.
        valid_attributes = {'title', 'content', 'content_type', 'heading_level', 'icon'}
        self.verify(
            expression=attribute in valid_attributes,
            error_code=const.KB_INVALID_SECTION_ATTRIBUTE_ID,
            message=f'Invalid section attribute: {attribute}',
            attribute=attribute,
        )

        # Validate content_type values.
        if attribute == 'content_type':
            valid_types = {'text', 'markdown', 'code'}
            self.verify(
                expression=value in valid_types,
                error_code=const.KB_INVALID_CONTENT_TYPE_ID,
                message=f'Invalid content type: {value}',
                content_type=value,
            )

        # When updating the title, ensure a non-empty value.
        if attribute == 'title':
            self.verify(
                expression=isinstance(value, str) and bool(value.strip()),
                error_code=const.KB_INVALID_SECTION_ATTRIBUTE_ID,
                message='A section title is required.',
            )

        # Require document_id to locate the section group.
        document_id = kwargs.get('document_id')
        self.verify(
            expression=document_id is not None,
            error_code=const.KB_DOCUMENT_SECTION_NOT_FOUND_ID,
            message='document_id is required to locate the section.',
            section_id=id,
        )

        # Retrieve all sections for the document and find the target.
        sections = self.document_service.get_sections(document_id)
        section = next((s for s in sections if s.id == id), None)

        # Verify the section exists.
        self.verify(
            expression=section is not None,
            error_code=const.KB_DOCUMENT_SECTION_NOT_FOUND_ID,
            section_id=id,
        )

        # Apply the requested update.
        if attribute == 'title':
            section.rename(value)
        elif attribute == 'content':
            # Re-parse the markdown content into paragraphs/segments.
            paragraphs = parse_content_to_paragraphs(value or '', section.id)
            section.set_paragraphs(paragraphs)
        elif attribute == 'content_type':
            section.set_content_type(value)
        elif attribute == 'heading_level':
            section.set_heading_level(value)
        elif attribute == 'icon':
            section.set_icon(value)

        # Persist the updated section.
        self.document_service.save_section(section)

        # Return the updated section.
        return section


# ** event: remove_document_section
class RemoveDocumentSection(DomainEvent):
    '''
    Event to remove a section from a document (idempotent).
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the RemoveDocumentSection event.

        :param document_service: The document service for deletion.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a section by ID.

        :param id: The section identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The removed section ID.
        :rtype: str
        '''

        # Delete the section (idempotent).
        self.document_service.delete_section(id)

        # Return the section identifier.
        return id


# ** event: reorder_document_sections
class ReorderDocumentSections(DomainEvent):
    '''
    Event to reorder sections within a document.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the ReorderDocumentSections event.

        :param document_service: The document service for persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['document_id', 'section_ids'])
    def execute(self,
            document_id: str,
            section_ids: List[str],
            **kwargs,
        ) -> str:
        '''
        Reorder sections within a document.

        :param document_id: The parent document identifier.
        :type document_id: str
        :param section_ids: The section IDs in the desired order.
        :type section_ids: List[str]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document identifier.
        :rtype: str
        '''

        # Verify the document exists.
        self.verify(
            expression=self.document_service.exists(document_id),
            error_code=const.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=document_id,
        )

        # Delegate reordering to the service.
        self.document_service.reorder_sections(document_id, section_ids)

        # Return the document identifier.
        return document_id
