"""tiferet_kb Tag Events"""

# *** imports

# ** core
from typing import Any, List

# ** app
from tiferet.events import DomainEvent

from .. import a
from ..domain.tag import Tag
from ..interfaces.document import DocumentService
from ..interfaces.tag import TagService
from ..mappers.tag import TagAggregate

# *** events

# ** event: add_tag
class AddTag(DomainEvent):
    '''
    Event to create a shared tag label.

    The id is stored as given. Uniqueness is the id, not the name.
    '''

    # * attribute: tag_service
    tag_service: TagService

    # * init
    def __init__(self, tag_service: TagService):
        '''
        Initialize the AddTag event.

        :param tag_service: The tag service for persistence.
        :type tag_service: TagService
        '''

        # Set the tag service dependency.
        self.tag_service = tag_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name'])
    def execute(self,
            id: str,
            name: str,
            color: str | None = None,
            **kwargs,
        ) -> Tag:
        '''
        Create a new tag.

        :param id: The caller-supplied tag identifier.
        :type id: str
        :param name: The display name for the tag.
        :type name: str
        :param color: Optional color string.
        :type color: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created tag.
        :rtype: Tag
        '''

        # Create the tag aggregate. The id is stored as given.
        tag = TagAggregate(
            id=id,
            name=name,
            color=color,
        )

        # Verify no duplicate tag id exists.
        self.verify(
            expression=not self.tag_service.exists(tag.id),
            error_code=a.errors.KB_TAG_ALREADY_EXISTS_ID,
            message=f'Tag with ID {tag.id} already exists.',
            id=tag.id,
        )

        # Persist the new tag.
        self.tag_service.save(tag)

        # Return the created tag.
        return tag

# ** event: get_tag
class GetTag(DomainEvent):
    '''
    Event to retrieve a tag by its identifier.
    '''

    # * attribute: tag_service
    tag_service: TagService

    # * init
    def __init__(self, tag_service: TagService):
        '''
        Initialize the GetTag event.

        :param tag_service: The tag service for retrieval.
        :type tag_service: TagService
        '''

        # Set the tag service dependency.
        self.tag_service = tag_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> Tag:
        '''
        Retrieve a tag by ID.

        :param id: The tag identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The retrieved tag.
        :rtype: Tag
        '''

        # Retrieve the tag from the service.
        tag = self.tag_service.get(id)

        # Verify that the tag exists.
        self.verify(
            expression=tag is not None,
            error_code=a.errors.KB_TAG_NOT_FOUND_ID,
            tag_id=id,
        )

        # Return the retrieved tag.
        return tag

# ** event: list_tags
class ListTags(DomainEvent):
    '''
    Event to list every tag label. There is no filter.
    '''

    # * attribute: tag_service
    tag_service: TagService

    # * init
    def __init__(self, tag_service: TagService):
        '''
        Initialize the ListTags event.

        :param tag_service: The tag service for listing.
        :type tag_service: TagService
        '''

        # Set the tag service dependency.
        self.tag_service = tag_service

    # * method: execute
    def execute(self, **kwargs) -> List[Tag]:
        '''
        List all tags.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A list of tags.
        :rtype: List[Tag]
        '''

        # Delegate to the tag service.
        return self.tag_service.list()

# ** event: update_tag
class UpdateTag(DomainEvent):
    '''
    Event to update an existing tag's name or color.

    The id is not an updatable attribute. Color may be cleared.
    '''

    # * attribute: tag_service
    tag_service: TagService

    # * init
    def __init__(self, tag_service: TagService):
        '''
        Initialize the UpdateTag event.

        :param tag_service: The tag service for retrieval and persistence.
        :type tag_service: TagService
        '''

        # Set the tag service dependency.
        self.tag_service = tag_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'attribute'])
    def execute(self,
            id: str,
            attribute: str,
            value: Any = None,
            **kwargs,
        ) -> Tag:
        '''
        Update a tag attribute.

        :param id: The tag identifier.
        :type id: str
        :param attribute: The attribute to update (name or color).
        :type attribute: str
        :param value: The new value for the attribute.
        :type value: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The updated tag.
        :rtype: Tag
        '''

        # Validate that the attribute is supported. The id is not updatable.
        valid_attributes = {'name', 'color'}
        self.verify(
            expression=attribute in valid_attributes,
            error_code=a.errors.KB_INVALID_TAG_ATTRIBUTE_ID,
            message=f'Invalid tag attribute: {attribute}',
            attribute=attribute,
        )

        # When updating the name, ensure a non-empty value is provided.
        if attribute == 'name':
            self.verify(
                expression=isinstance(value, str) and bool(value.strip()),
                error_code=a.errors.KB_INVALID_TAG_ATTRIBUTE_ID,
                message='A tag name is required when updating the name attribute.',
                attribute=attribute,
            )

        # Retrieve the tag from the service.
        tag = self.tag_service.get(id)

        # Verify that the tag exists.
        self.verify(
            expression=tag is not None,
            error_code=a.errors.KB_TAG_NOT_FOUND_ID,
            tag_id=id,
        )

        # Apply the requested update using aggregate mutation methods.
        if attribute == 'name':
            tag.rename(value)
        elif attribute == 'color':
            tag.set_color(value)

        # Persist the updated tag.
        self.tag_service.save(tag)

        # Return the updated tag.
        return tag

# ** event: remove_tag
class RemoveTag(DomainEvent):
    '''
    Event to remove a tag label.

    Refuses while any document still carries the tag. Does not untag those
    documents. Delete is idempotent when no document carries the id, including
    when the label is already gone.
    '''

    # * attribute: tag_service
    tag_service: TagService

    # * init
    def __init__(self, tag_service: TagService):
        '''
        Initialize the RemoveTag event.

        :param tag_service: The tag service for carrier checks and deletion.
        :type tag_service: TagService
        '''

        # Set the tag service dependency.
        self.tag_service = tag_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a tag by ID when no document carries it.

        :param id: The tag identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The removed tag ID.
        :rtype: str
        '''

        # Refuse while any association still names this tag.
        carriers = self.tag_service.list_document_ids(id)
        self.verify(
            expression=len(carriers) == 0,
            error_code=a.errors.KB_TAG_IN_USE_ID,
            message=f'Tag {id} is carried by existing documents.',
            id=id,
        )

        # Delete the label. A missing label is not an error.
        self.tag_service.delete(id)

        # Return the tag identifier.
        return id

# ** event: tag_document
class TagDocument(DomainEvent):
    '''
    Event to record that a document carries a tag.

    Checks the document first, then the tag. Both must exist. Repeating the
    pair does not create a second association and does not raise. Does not
    load or rewrite section passages, and does not write ``category_id``.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * attribute: tag_service
    tag_service: TagService

    # * init
    def __init__(self, document_service: DocumentService, tag_service: TagService):
        '''
        Initialize the TagDocument event.

        :param document_service: The document service for the existence check.
        :type document_service: DocumentService
        :param tag_service: The tag service for the existence check and the association.
        :type tag_service: TagService
        '''

        # Set the document service dependency.
        self.document_service = document_service

        # Set the tag service dependency.
        self.tag_service = tag_service

    # * method: execute
    @DomainEvent.parameters_required(['document_id', 'tag_id'])
    def execute(self, document_id: str, tag_id: str, **kwargs) -> str:
        '''
        Tag a document.

        :param document_id: The document identifier.
        :type document_id: str
        :param tag_id: The tag identifier.
        :type tag_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document identifier.
        :rtype: str
        '''

        # Check the document first. exists does not load section passages.
        self.verify(
            expression=self.document_service.exists(document_id),
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=document_id,
        )

        # Then require the tag label.
        self.verify(
            expression=self.tag_service.get(tag_id) is not None,
            error_code=a.errors.KB_TAG_NOT_FOUND_ID,
            tag_id=tag_id,
        )

        # Record one association. A repeat is a no-op.
        self.tag_service.tag_document(document_id, tag_id)

        # Return the document identifier.
        return document_id

# ** event: untag_document
class UntagDocument(DomainEvent):
    '''
    Event to remove a document–tag association.

    Succeeds when the association is already absent. Does not require the
    tag label to still exist, and does not delete the tag.
    '''

    # * attribute: tag_service
    tag_service: TagService

    # * init
    def __init__(self, tag_service: TagService):
        '''
        Initialize the UntagDocument event.

        :param tag_service: The tag service for the association.
        :type tag_service: TagService
        '''

        # Set the tag service dependency.
        self.tag_service = tag_service

    # * method: execute
    @DomainEvent.parameters_required(['document_id', 'tag_id'])
    def execute(self, document_id: str, tag_id: str, **kwargs) -> str:
        '''
        Untag a document.

        :param document_id: The document identifier.
        :type document_id: str
        :param tag_id: The tag identifier.
        :type tag_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document identifier.
        :rtype: str
        '''

        # Remove the association when present. Absent is success.
        self.tag_service.untag_document(document_id, tag_id)

        # Return the document identifier.
        return document_id

# ** event: list_document_tags
class ListDocumentTags(DomainEvent):
    '''
    Event to list the tags a document carries.

    Raises when the document does not exist. An existing document that
    carries none returns an empty list. Does not add a tags field to Document.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * attribute: tag_service
    tag_service: TagService

    # * init
    def __init__(self, document_service: DocumentService, tag_service: TagService):
        '''
        Initialize the ListDocumentTags event.

        :param document_service: The document service for the existence check.
        :type document_service: DocumentService
        :param tag_service: The tag service for the association read.
        :type tag_service: TagService
        '''

        # Set the document service dependency.
        self.document_service = document_service

        # Set the tag service dependency.
        self.tag_service = tag_service

    # * method: execute
    @DomainEvent.parameters_required(['document_id'])
    def execute(self, document_id: str, **kwargs) -> List[Tag]:
        '''
        List tags carried by a document.

        :param document_id: The document identifier.
        :type document_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The tags that document carries.
        :rtype: List[Tag]
        '''

        # A missing document is an error, not an empty list.
        self.verify(
            expression=self.document_service.exists(document_id),
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=document_id,
        )

        # Return the tags the document carries. None is an empty list.
        return self.tag_service.list_tags_for_document(document_id)
