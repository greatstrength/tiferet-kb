"""tiferet_kb Document Link Events"""

# *** imports

# ** core
from typing import List

# ** app
from tiferet.events import DomainEvent

from .. import a
from ..domain.document_link import DocumentLink
from ..interfaces.document import DocumentService
from ..mappers.document_link import DocumentLinkAggregate, DocumentLinkTableObject

# *** events

# ** event: document_link_event
class DocumentLinkEvent(DomainEvent):
    '''
    Base event for a pointer from one document to another.

    Link commands share the document service. They do not open a second
    file and they do not grow a second repository.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService) -> None:
        '''
        Initialize the document link event.

        :param document_service: The document service for persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

# ** event: add_document_link
class AddDocumentLink(DocumentLinkEvent):
    '''
    Event to store one directional link between two documents in this file.

    The type is an open string. The documented names are published as
    constants; any other non-empty string that fits the column is stored
    as given. Add does not write the reverse row.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['source_id', 'target_id'])
    def execute(self,
            source_id: str,
            target_id: str,
            link_type: str | None = None,
            id: str | None = None,
            **kwargs,
        ) -> DocumentLink:
        '''
        Add a document link after the type, the endpoints, and the column fit.

        ``created_at`` is derived. A caller-supplied timestamp is ignored.
        A failed check writes nothing.

        :param source_id: The document the link starts from.
        :type source_id: str
        :param target_id: The document the link points at.
        :type target_id: str
        :param link_type: The relationship name. Ends are stripped; case is kept.
        :type link_type: str | None
        :param id: Optional explicit link identifier.
        :type id: str | None
        :param kwargs: Additional keyword arguments. ``created_at`` is not read.
        :type kwargs: dict
        :return: The stored link.
        :rtype: DocumentLink
        '''

        # Strip the type. Empty after strip is invalid, not a missing parameter.
        if not isinstance(link_type, str):
            link_type = ''
        else:
            link_type = link_type.strip()

        # Reject an empty type or one that would be clipped to the title width.
        self.verify(
            expression=bool(link_type) and DocumentLinkTableObject.value_fits(
                link_type,
                DocumentLinkTableObject.type_width(),
            ),
            error_code=a.errors.KB_INVALID_DOCUMENT_LINK_ID,
            message='Invalid document link type.',
            link_type=link_type,
        )

        # A blank id is omitted and derived. A supplied id that does not fit is rejected.
        supplied_id = None
        if isinstance(id, str) and id.strip():
            supplied_id = id
            self.verify(
                expression=DocumentLinkTableObject.value_fits(
                    supplied_id,
                    DocumentLinkTableObject.identifier_width(),
                ),
                error_code=a.errors.KB_INVALID_DOCUMENT_LINK_ID,
                message='Invalid document link id.',
                id=supplied_id,
            )

        # Both documents must exist. Check the source first, then the target.
        self.verify(
            expression=self.document_service.exists(source_id),
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
            message=f'Document not found: {source_id}',
            document_id=source_id,
        )
        self.verify(
            expression=self.document_service.exists(target_id),
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
            message=f'Document not found: {target_id}',
            document_id=target_id,
        )

        # A self-link is rejected only after both endpoints exist.
        self.verify(
            expression=source_id != target_id,
            error_code=a.errors.KB_INVALID_DOCUMENT_LINK_ID,
            message='A document link cannot point at its source.',
            source_id=source_id,
            target_id=target_id,
        )

        # Build the link. The timestamp is derived; kwargs are not consulted.
        link_kwargs = dict(
            source_id=source_id,
            target_id=target_id,
            link_type=link_type,
        )
        if supplied_id:
            link_kwargs['id'] = supplied_id
        link = DocumentLinkAggregate(**link_kwargs)

        # Persist. The repository refuses a duplicate id or triple and does not insert first.
        return self.document_service.add_link(link)

# ** event: remove_document_link
class RemoveDocumentLink(DocumentLinkEvent):
    '''
    Event to remove one document link by its identifier.

    Remove is idempotent. It does not delete either document, and it does
    not add or remove a reverse row.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a document link by id.

        :param id: The link identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The link identifier.
        :rtype: str
        '''

        # Delete the row. A missing row still succeeds.
        self.document_service.remove_link(id)

        # Return the identifier, same contract as RemoveDocument.
        return id

# ** event: list_document_links
class ListDocumentLinks(DocumentLinkEvent):
    '''
    Event to list the links for one document, outgoing, incoming, or both.

    The list returns links, not document headers. An omitted direction is
    both directions: outgoing rows, then incoming rows.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document_id'])
    def execute(self,
            document_id: str,
            direction: str | None = None,
            link_type: str | None = None,
            **kwargs,
        ) -> List[DocumentLink]:
        '''
        List links for a document.

        An omitted direction is ``both``. An empty type is invalid, not
        "every type". A missing link table is an empty list and is not created.

        :param document_id: The document whose links are listed.
        :type document_id: str
        :param direction: ``outgoing``, ``incoming``, or ``both``.
        :type direction: str | None
        :param link_type: Optional exact type filter. Ends are stripped.
        :type link_type: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The matching links.
        :rtype: List[DocumentLink]
        '''

        # Omitted direction asks what the document is tied to, in both directions.
        if direction is None:
            direction = a.core.DOCUMENT_LINK_BOTH

        # Any other direction fails and writes nothing.
        allowed = {
            a.core.DOCUMENT_LINK_OUTGOING,
            a.core.DOCUMENT_LINK_INCOMING,
            a.core.DOCUMENT_LINK_BOTH,
        }
        self.verify(
            expression=direction in allowed,
            error_code=a.errors.KB_INVALID_DOCUMENT_LINK_ID,
            message=f'Invalid document link direction: {direction}',
            direction=direction,
        )

        # An empty type is not "every type". Omitted means every type.
        if link_type is not None:
            if not isinstance(link_type, str):
                link_type = ''
            else:
                link_type = link_type.strip()
            self.verify(
                expression=bool(link_type),
                error_code=a.errors.KB_INVALID_DOCUMENT_LINK_ID,
                message='Invalid document link type.',
                link_type=link_type,
            )

        # The document must exist. A missing link table is not this failure.
        self.verify(
            expression=self.document_service.exists(document_id),
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
            message=f'Document not found: {document_id}',
            document_id=document_id,
        )

        # Delegate. The repository does not create the table on a read.
        return self.document_service.list_links(
            document_id,
            direction=direction,
            link_type=link_type,
        )
