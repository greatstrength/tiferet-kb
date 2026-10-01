"""tiferet_kb Document Events"""

# *** imports

# ** core
from typing import Any, List

# ** app
from tiferet.domain import ModelError
from tiferet.events import DomainEvent

from .. import a
from ..domain.document import Document, DocumentProperty, DocumentSection
from ..interfaces.document import DocumentService
from ..interfaces.tag import TagService
from ..mappers.document import (
    DocumentAggregate,
    DocumentPropertyTableObject,
    DocumentSectionAggregate,
)
from ..utils.markdown import parse_content_to_paragraphs

# *** functions

# ** function: cleared_owner_id
def cleared_owner_id(owner_id: str | None) -> str | None:
    '''
    Return a stored owner, or None when the caller omitted, emptied, or blanked it.

    :param owner_id: The caller-supplied owner identifier.
    :type owner_id: str | None
    :return: The owner to store, or None to clear.
    :rtype: str | None
    '''

    # A missing, empty, or whitespace-only value clears the owner.
    if not isinstance(owner_id, str) or not owner_id.strip():
        return None

    # Keep a non-empty owner exactly as supplied.
    return owner_id

# ** function: copy_paragraphs
def copy_paragraphs(paragraphs: List) -> List:
    '''
    Deep-copy a paragraph list so a snapshot does not share the live list.

    :param paragraphs: The paragraphs to copy.
    :type paragraphs: List
    :return: A new list of copied paragraphs.
    :rtype: List
    '''

    # Copy each paragraph, including its segments and identifiers.
    return [paragraph.model_copy(deep=True) for paragraph in paragraphs]

# ** function: revision_number
def revision_number(value: Any) -> int | None:
    '''
    Coerce a revision number, or return None when it is not an integer.

    :param value: The caller-supplied number.
    :type value: Any
    :return: The integer, which may be less than 1, or None.
    :rtype: int | None
    '''

    # Booleans are integers; they are not revision numbers.
    if isinstance(value, bool) or value is None:
        return None

    # Accept an int as given.
    if isinstance(value, int):
        return value

    # Accept a numeric string, including a negative one.
    if isinstance(value, str):
        text = value.strip()
        if text.lstrip('-').isdigit() and text not in ('', '-'):
            return int(text)

    # Any other shape is not a revision number.
    return None

# ** function: locator_present
def locator_present(document_id: Any, section_id: Any) -> bool:
    '''
    Report whether both identifiers are non-blank strings.

    :param document_id: The document identifier.
    :type document_id: Any
    :param section_id: The section identifier.
    :type section_id: Any
    :return: True when both are present.
    :rtype: bool
    '''

    # A missing or blank identifier must not start a document walk.
    return (
        isinstance(document_id, str) and bool(document_id.strip())
        and isinstance(section_id, str) and bool(section_id.strip())
    )

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
            visibility: str | None = None,
            owner_id: str | None = None,
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
        :param visibility: Optional visibility token. Omitted reads as public.
        :type visibility: str | None
        :param owner_id: Optional opaque owner. Empty or whitespace clears it.
        :type owner_id: str | None
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
        if visibility is not None:
            doc_kwargs['visibility'] = visibility
        if owner_id is not None:
            doc_kwargs['owner_id'] = cleared_owner_id(owner_id)

        # Create the document aggregate (UUID and timestamps auto-derived).
        document = DocumentAggregate(**doc_kwargs)

        # Verify no duplicate document exists.
        self.verify(
            expression=not self.document_service.exists(document.id),
            error_code=a.errors.KB_DOCUMENT_ALREADY_EXISTS_ID,
            message=f'Document with ID {document.id} already exists.',
            id=document.id,
        )

        # Validate status if provided.
        if status:
            valid_statuses = {'draft', 'published', 'archived'}
            self.verify(
                expression=status in valid_statuses,
                error_code=a.errors.KB_INVALID_DOCUMENT_STATUS_ID,
                message=f'Invalid document status: {status}',
                status=status,
            )

        # A supplied visibility must be one of the three exact tokens.
        if visibility is not None:
            self.verify(
                expression=visibility in a.core.VISIBILITIES,
                error_code=a.errors.KB_INVALID_VISIBILITY_ID,
                message=a.errors.KB_INVALID_VISIBILITY_MESSAGE.format(visibility=visibility),
                visibility=visibility,
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
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=id,
        )

        # Return the retrieved document.
        return document

# ** event: list_documents
class ListDocuments(DomainEvent):
    '''
    Event to list documents with optional filters.

    ``tag_id`` is association membership, composed here. It is not a column
    on the document header. Omitted or empty means no tag condition.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * attribute: tag_service
    tag_service: TagService

    # * init
    def __init__(self, document_service: DocumentService, tag_service: TagService):
        '''
        Initialize the ListDocuments event.

        :param document_service: The document service for header filters.
        :type document_service: DocumentService
        :param tag_service: The tag service for association membership.
        :type tag_service: TagService
        '''

        # Set the document service dependency.
        self.document_service = document_service

        # Set the tag service dependency.
        self.tag_service = tag_service

    # * method: execute
    def execute(self,
            folder_id: str | None = None,
            category_id: str | None = None,
            status: str | None = None,
            title: str | None = None,
            include_properties: bool = False,
            property_name: str | None = None,
            property_value: Any = None,
            property_value_type: str | None = None,
            tag_id: str | None = None,
            visibility: str | None = None,
            owner_id: str | None = None,
            **kwargs,
        ) -> List[Document]:
        '''
        List documents with optional filters.

        Property arguments are always forwarded, including their defaults.
        This event does not pass ``include_sections``. When ``tag_id`` is
        set, the result is further limited to documents that carry that tag.
        A tag id that matches nothing yields an empty list, not an error.

        :param folder_id: Optional folder identifier to filter by.
        :type folder_id: str | None
        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :param status: Optional status to filter by.
        :type status: str | None
        :param title: Optional exact document title. Empty or omitted adds no condition.
        :type title: str | None
        :param include_properties: If True, each header carries its property bag.
        :type include_properties: bool
        :param property_name: Optional property name to match exactly.
        :type property_name: str | None
        :param property_value: Optional property value to match exactly.
        :type property_value: Any
        :param property_value_type: Optional declared type of the property value.
        :type property_value_type: str | None
        :param tag_id: Optional tag identifier. Empty means no tag condition.
        :type tag_id: str | None
        :param visibility: Optional visibility to filter by.
        :type visibility: str | None
        :param owner_id: Optional owner identifier to filter by.
        :type owner_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A list of document headers.
        :rtype: List[Document]
        '''

        # Reject a partial or ill-typed property filter before the service call.
        try:
            DocumentProperty.filter_rejection(
                property_name,
                property_value,
                property_value_type,
            )
        except ModelError as error:
            self.raise_error(
                error.error_code,
                name=property_name,
                value_type=property_value_type,
            )

        # An unrecognized visibility is not an empty list and not a status filter.
        if visibility is not None:
            self.verify(
                expression=visibility in a.core.VISIBILITIES,
                error_code=a.errors.KB_INVALID_VISIBILITY_ID,
                message=a.errors.KB_INVALID_VISIBILITY_MESSAGE.format(visibility=visibility),
                visibility=visibility,
            )

        # Header filters stay on the document service. Always forward title,
        # property arguments, and access filters. Do not pass tag_id or include_sections.
        documents = self.document_service.list(
            folder_id=folder_id,
            category_id=category_id,
            status=status,
            title=title,
            include_properties=include_properties,
            property_name=property_name,
            property_value=property_value,
            property_value_type=property_value_type,
            visibility=visibility,
            owner_id=owner_id,
        )

        # An omitted or empty tag id is no tag condition.
        if not tag_id:
            return documents

        # Intersect headers with association membership. One tag id per call.
        carrier_ids = set(self.tag_service.list_document_ids(tag_id))
        return [document for document in documents if document.id in carrier_ids]

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
            error_code=a.errors.KB_INVALID_DOCUMENT_ATTRIBUTE_ID,
            message=f'Invalid document attribute: {attribute}',
            attribute=attribute,
        )

        # Validate status values.
        if attribute == 'status':
            valid_statuses = {'draft', 'published', 'archived'}
            self.verify(
                expression=value in valid_statuses,
                error_code=a.errors.KB_INVALID_DOCUMENT_STATUS_ID,
                message=f'Invalid document status: {value}',
                status=value,
            )

        # When updating the title, ensure a non-empty value.
        if attribute == 'title':
            self.verify(
                expression=isinstance(value, str) and bool(value.strip()),
                error_code=a.errors.KB_INVALID_DOCUMENT_ATTRIBUTE_ID,
                message='A document title is required.',
            )

        # Retrieve the document from the service.
        document = self.document_service.get(id)

        # Verify that the document exists.
        self.verify(
            expression=document is not None,
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
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

# ** event: set_document_visibility
class SetDocumentVisibility(DomainEvent):
    '''
    Event to set visibility and owner on an existing document.

    Visibility is restated on every call. An omitted, empty, or
    whitespace-only owner clears the stored owner. The call does not
    create the document and does not change its other header fields.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the SetDocumentVisibility event.

        :param document_service: The document service for retrieval and persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'visibility'])
    def execute(self,
            id: str,
            visibility: str,
            owner_id: str | None = None,
            **kwargs,
        ) -> Document:
        '''
        Set visibility and owner on an existing document.

        :param id: The document identifier.
        :type id: str
        :param visibility: The visibility token (public, private, or restricted).
        :type visibility: str
        :param owner_id: Optional owner. Omitted, empty, or whitespace clears it.
        :type owner_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The updated document.
        :rtype: Document
        '''

        # Reject a token outside the closed set, including a status token.
        self.verify(
            expression=visibility in a.core.VISIBILITIES,
            error_code=a.errors.KB_INVALID_VISIBILITY_ID,
            message=a.errors.KB_INVALID_VISIBILITY_MESSAGE.format(visibility=visibility),
            visibility=visibility,
        )

        # Retrieve the document. This event does not create one.
        document = self.document_service.get(id)
        self.verify(
            expression=document is not None,
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=id,
        )

        # Set the access fields. Other header fields stay as they were.
        document.set_visibility(visibility)
        document.set_owner(cleared_owner_id(owner_id))

        # Persist the header. The setters already refreshed updated_at.
        self.document_service.save(document)

        # Return the updated document.
        return document

# ** event: remove_document
class RemoveDocument(DomainEvent):
    '''
    Event to remove a document by ID (idempotent, cascading sections).

    Clears that document's tag associations first, so a deleted document
    cannot leave ``RemoveTag`` refusing with nothing left to untag.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * attribute: tag_service
    tag_service: TagService

    # * init
    def __init__(self, document_service: DocumentService, tag_service: TagService):
        '''
        Initialize the RemoveDocument event.

        :param document_service: The document service for deletion.
        :type document_service: DocumentService
        :param tag_service: The tag service for association cleanup.
        :type tag_service: TagService
        '''

        # Set the document service dependency.
        self.document_service = document_service

        # Set the tag service dependency.
        self.tag_service = tag_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a document and all its sections by ID.

        Association cleanup is idempotent when the document carries no tags.

        :param id: The document identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The removed document ID.
        :rtype: str
        '''

        # Drop associations before the document, so a retry cannot strand a tag.
        self.tag_service.clear_document(id)

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
            error_code=a.errors.KB_INVALID_CONTENT_TYPE_ID,
            message=f'Invalid content type: {content_type}',
            content_type=content_type,
        )

        # Verify the parent document exists.
        self.verify(
            expression=self.document_service.exists(document_id),
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
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
            error_code=a.errors.KB_INVALID_SECTION_ATTRIBUTE_ID,
            message=f'Invalid section attribute: {attribute}',
            attribute=attribute,
        )

        # Validate content_type values.
        if attribute == 'content_type':
            valid_types = {'text', 'markdown', 'code'}
            self.verify(
                expression=value in valid_types,
                error_code=a.errors.KB_INVALID_CONTENT_TYPE_ID,
                message=f'Invalid content type: {value}',
                content_type=value,
            )

        # When updating the title, ensure a non-empty value.
        if attribute == 'title':
            self.verify(
                expression=isinstance(value, str) and bool(value.strip()),
                error_code=a.errors.KB_INVALID_SECTION_ATTRIBUTE_ID,
                message='A section title is required.',
            )

        # Require document_id to locate the section group.
        document_id = kwargs.get('document_id')
        self.verify(
            expression=document_id is not None,
            error_code=a.errors.KB_DOCUMENT_SECTION_NOT_FOUND_ID,
            message='document_id is required to locate the section.',
            section_id=id,
        )

        # Retrieve all sections for the document and find the target.
        sections = self.document_service.get_sections(document_id)
        section = next((s for s in sections if s.id == id), None)

        # Verify the section exists.
        self.verify(
            expression=section is not None,
            error_code=a.errors.KB_DOCUMENT_SECTION_NOT_FOUND_ID,
            section_id=id,
        )

        # Apply the requested update.
        if attribute == 'content':
            # Compare parsed passages here. The repository does not decide.
            parsed = parse_content_to_paragraphs(value or '', section.id)
            if section.matches_paragraphs(parsed):
                return section

            # Snapshot the stored passages before they are replaced.
            self.document_service.append_section_revision(
                document_id=section.document_id,
                section_id=section.id,
                title=section.title,
                content_type=section.content_type,
                paragraphs=copy_paragraphs(section.paragraphs),
            )
            section.set_paragraphs(parsed)
        elif attribute == 'title':
            section.rename(value)
        elif attribute == 'content_type':
            section.set_content_type(value)
        elif attribute == 'heading_level':
            section.set_heading_level(value)
        elif attribute == 'icon':
            section.set_icon(value)

        # Persist the updated section. An identical content write returned above.
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
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=document_id,
        )

        # Delegate reordering to the service.
        self.document_service.reorder_sections(document_id, section_ids)

        # Return the document identifier.
        return document_id

# ** event: set_document_property
class SetDocumentProperty(DomainEvent):
    '''
    Event to set one named typed value on an existing document.

    A second set of the same name replaces the value and the type. The
    header columns are not aliases of property names.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the SetDocumentProperty event.

        :param document_service: The document service for persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['document_id'])
    def execute(self,
            document_id: str,
            name: str = None,
            value: Any = None,
            value_type: str = None,
            **kwargs,
        ) -> DocumentProperty:
        '''
        Set one property on an existing document.

        :param document_id: The document identifier.
        :type document_id: str
        :param name: The property name. Stripped once.
        :type name: str
        :param value: The property value. Empty string, 0, and False are values.
        :type value: Any
        :param value_type: The declared type: string, number, or boolean.
        :type value_type: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The stored property.
        :rtype: DocumentProperty
        '''

        # Raise the asset error before the domain object is constructed.
        try:
            DocumentProperty.rejection(name, value, value_type)
        except ModelError as error:
            self.raise_error(error.error_code, name=name, value_type=value_type)

        # A name or string the aligned column cannot store fails as a catalog error.
        stored_name = name.strip()
        name_width = DocumentPropertyTableObject._H5_TYPES['name'].itemsize
        if len(stored_name.encode('utf-8')) > name_width:
            self.raise_error(a.errors.KB_INVALID_PROPERTY_NAME_ID, name=name)
        if value_type == 'string' and isinstance(value, str):
            value_width = DocumentPropertyTableObject._H5_TYPES['value_string'].itemsize
            if len(value.encode('utf-8')) > value_width:
                self.raise_error(
                    a.errors.KB_INVALID_PROPERTY_VALUE_ID,
                    value_type=value_type,
                )

        # Do not create a document for a property write.
        self.verify(
            expression=self.document_service.exists(document_id),
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=document_id,
        )

        # Persist the property. The service replaces the same name.
        return self.document_service.set_property(
            document_id,
            name,
            value,
            value_type,
        )

# ** event: remove_document_property
class RemoveDocumentProperty(DomainEvent):
    '''
    Event to remove one named value from a document.

    A missing row or a missing document succeeds and returns the name.
    An idempotent remove does not move the document clock.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the RemoveDocumentProperty event.

        :param document_service: The document service for persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['document_id', 'name'])
    def execute(self,
            document_id: str,
            name: str,
            **kwargs,
        ) -> str:
        '''
        Remove one property by name.

        :param document_id: The document identifier.
        :type document_id: str
        :param name: The property name. Stripped once for the lookup.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The stripped property name.
        :rtype: str
        '''

        # Look up the stored form. A missing row still returns that name.
        stored = name.strip()
        self.document_service.remove_property(document_id, stored)

        # Return the name. Absence is success.
        return stored

# ** event: list_document_section_revisions
class ListDocumentSectionRevisions(DomainEvent):
    '''
    Hands back a section's passage snapshots, newest number first.

    The live section is not a row. A section that has never been snapshotted
    lists as empty.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the ListDocumentSectionRevisions event.

        :param document_service: The document service for retrieval.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    def execute(self,
            id: str | None = None,
            document_id: str | None = None,
            **kwargs,
        ) -> List:
        '''
        List revisions for one section, highest number first.

        :param id: The section identifier.
        :type id: str | None
        :param document_id: The parent document identifier.
        :type document_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The section's revisions. Not a markdown string.
        :rtype: List
        '''

        # A missing document id must not walk every document group.
        self.verify(
            expression=locator_present(document_id, id),
            error_code=a.errors.KB_DOCUMENT_SECTION_NOT_FOUND_ID,
            message='document_id and section id are required to list revisions.',
            section_id=id,
        )

        # A missing section is not an empty history.
        sections = self.document_service.get_sections(document_id)
        section = next((item for item in sections if item.id == id), None)
        self.verify(
            expression=section is not None,
            error_code=a.errors.KB_DOCUMENT_SECTION_NOT_FOUND_ID,
            section_id=id,
        )

        # Return the snapshots. The live section is not an item.
        return self.document_service.list_section_revisions(document_id, id)

# ** event: restore_document_section_revision
class RestoreDocumentSectionRevision(DomainEvent):
    '''
    Puts a chosen snapshot's paragraphs back on the section.

    The passages that write replaces are snapshotted first, even when they
    already match the snapshot. The heading and content type stay as they are.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the RestoreDocumentSectionRevision event.

        :param document_service: The document service for retrieval and persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    def execute(self,
            id: str | None = None,
            document_id: str | None = None,
            number: Any = None,
            **kwargs,
        ) -> DocumentSection:
        '''
        Restore a section's paragraphs from a numbered revision.

        :param id: The section identifier.
        :type id: str | None
        :param document_id: The parent document identifier.
        :type document_id: str | None
        :param number: The revision number to restore.
        :type number: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The section with the snapshot's paragraphs.
        :rtype: DocumentSection
        '''

        # A missing document id must not walk every document group.
        self.verify(
            expression=locator_present(document_id, id),
            error_code=a.errors.KB_DOCUMENT_SECTION_NOT_FOUND_ID,
            message='document_id and section id are required to restore a revision.',
            section_id=id,
        )

        # A missing section writes nothing.
        sections = self.document_service.get_sections(document_id)
        section = next((item for item in sections if item.id == id), None)
        self.verify(
            expression=section is not None,
            error_code=a.errors.KB_DOCUMENT_SECTION_NOT_FOUND_ID,
            section_id=id,
        )

        # A missing or non-positive number is not a revision.
        chosen = revision_number(number)
        self.verify(
            expression=chosen is not None and chosen >= 1,
            error_code=a.errors.KB_SECTION_REVISION_NOT_FOUND_ID,
            message=f'Section revision not found: {number}',
            section_id=id,
            number=number,
        )

        # Load the named snapshot before any write.
        revision = self.document_service.get_section_revision(document_id, id, chosen)
        self.verify(
            expression=revision is not None,
            error_code=a.errors.KB_SECTION_REVISION_NOT_FOUND_ID,
            message=f'Section revision not found: {chosen}',
            section_id=id,
            number=chosen,
        )

        # Snapshot the current passages first, even when the words already match.
        self.document_service.append_section_revision(
            document_id=section.document_id,
            section_id=section.id,
            title=section.title,
            content_type=section.content_type,
            paragraphs=copy_paragraphs(section.paragraphs),
        )

        # Put the snapshot's paragraph model back, identifiers included.
        section.set_paragraphs(copy_paragraphs(revision.paragraphs))
        self.document_service.save_section(section)

        # Return the section. Heading, icon, and position were not written.
        return section
