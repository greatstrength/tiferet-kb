"""tiferet_kb Section Comment Events"""

# *** imports

# ** core
from typing import List
from uuid import uuid4

# ** app
from tiferet.events import DomainEvent

from .. import a
from ..domain.comment import AUTHOR_MAX_LENGTH, TEXT_MAX_LENGTH, SectionComment
from ..interfaces.document import DocumentService
from ..mappers.comment import SectionCommentAggregate

# *** events

# ** event: comment_event
class CommentEvent(DomainEvent):
    '''
    Base event for a plain-text note on a section.

    The note is adjacent to the section, as a stored vector is adjacent.
    These events do not parse the note into passages and do not attach it
    to the section model.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService) -> None:
        '''
        Initialize with the document service that stores section comments.

        :param document_service: The document service dependency.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: _require_section
    def _require_section(self, document_id: str, section_id: str) -> None:
        '''
        Verify the document exists and the section is one of its sections.

        :param document_id: The document identifier.
        :type document_id: str
        :param section_id: The section identifier.
        :type section_id: str
        '''

        # A missing document is not an empty comment list.
        self.verify(
            expression=self.document_service.exists(document_id),
            error_code=a.errors.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=document_id,
        )

        # The section must belong to that document.
        sections = self.document_service.get_sections(document_id)
        self.verify(
            expression=any(section.id == section_id for section in sections),
            error_code=a.errors.KB_DOCUMENT_SECTION_NOT_FOUND_ID,
            section_id=section_id,
        )

    # * method: _clean_comment_field
    def _clean_comment_field(self, value: str | None, field: str, limit: int) -> str:
        '''
        Strip a comment field and reject an empty or over-long value.

        :param value: The raw caller value.
        :type value: str | None
        :param field: The field name, used in the error context.
        :type field: str
        :param limit: The maximum stored length, in characters.
        :type limit: int
        :return: The stripped value to store.
        :rtype: str
        '''

        # Reject a missing, blank, or over-long value. Do not truncate.
        cleaned = value.strip() if isinstance(value, str) else ''
        self.verify(
            expression=bool(cleaned) and len(cleaned) <= limit,
            error_code=a.errors.KB_INVALID_SECTION_COMMENT_ID,
            message=f'Invalid section comment {field}.',
            field=field,
        )
        return cleaned

    # * method: _require_parent
    def _require_parent(self,
            section_id: str,
            comment_id: str,
            parent_id: str | None,
        ) -> str | None:
        '''
        Accept an omitted parent, or a parent comment on the same section.

        :param section_id: The section being commented.
        :type section_id: str
        :param comment_id: The new comment identifier.
        :type comment_id: str
        :param parent_id: The caller-supplied parent identifier, if any.
        :type parent_id: str | None
        :return: The stripped parent id, or None when omitted.
        :rtype: str | None
        '''

        # An omitted or blank parent is stored as absent.
        parent_key = parent_id.strip() if isinstance(parent_id, str) else ''
        if not parent_key:
            return None

        # A comment cannot name itself. Parent id is set only on add, so this is the cycle check.
        self.verify(
            expression=parent_key != comment_id,
            error_code=a.errors.KB_INVALID_SECTION_COMMENT_ID,
            message='A section comment cannot reply to itself.',
            parent_id=parent_key,
        )

        # The parent must already be a comment on this section, including a reply.
        comments = self.document_service.list_comments(section_id)
        parent = next((item for item in comments if item.id == parent_key), None)
        self.verify(
            expression=parent is not None,
            error_code=a.errors.KB_INVALID_SECTION_COMMENT_ID,
            message='Parent comment is not on this section.',
            parent_id=parent_key,
        )
        return parent_key

# ** event: add_section_comment
class AddSectionComment(CommentEvent):
    '''
    Event to attach a new plain-text note to a section.

    Add inserts. It does not replace an existing note, and it does not
    parse the note into paragraphs.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document_id', 'section_id'])
    def execute(self,
            document_id: str,
            section_id: str,
            author: str | None = None,
            text: str | None = None,
            parent_id: str | None = None,
            id: str | None = None,
            created_at: str | None = None,
            **kwargs,
        ) -> SectionComment:
        '''
        Add a section comment.

        :param document_id: The document identifier.
        :type document_id: str
        :param section_id: The section identifier.
        :type section_id: str
        :param author: The caller-supplied author string.
        :type author: str | None
        :param text: The plain-text note.
        :type text: str | None
        :param parent_id: Optional parent comment identifier on the same section.
        :type parent_id: str | None
        :param id: Optional explicit comment identifier.
        :type id: str | None
        :param created_at: Optional creation timestamp. Stored as given.
        :type created_at: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created comment.
        :rtype: SectionComment
        '''

        # The document and section must exist before any row is written.
        self._require_section(document_id, section_id)

        # Store the stripped author and text. Over-long values are rejected, not truncated.
        author_value = self._clean_comment_field(author, 'author', AUTHOR_MAX_LENGTH)
        text_value = self._clean_comment_field(text, 'text', TEXT_MAX_LENGTH)

        # Derive the id before the parent check so a self-reply can be rejected.
        comment_id = id.strip() if isinstance(id, str) and id.strip() else str(uuid4())
        parent_key = self._require_parent(section_id, comment_id, parent_id)

        # Build the comment. Markdown in text is not parsed.
        comment_kwargs = dict(
            id=comment_id,
            document_id=document_id,
            section_id=section_id,
            author=author_value,
            text=text_value,
        )
        if isinstance(created_at, str) and created_at.strip():
            comment_kwargs['created_at'] = created_at.strip()
        if parent_key:
            comment_kwargs['parent_id'] = parent_key
        comment = SectionCommentAggregate(**comment_kwargs)

        # Insert only. A second add must not replace text.
        inserted = self.document_service.add_comment(comment)
        self.verify(
            expression=inserted,
            error_code=a.errors.KB_SECTION_COMMENT_ALREADY_EXISTS_ID,
            message=f'Section comment with ID {comment.id} already exists.',
            id=comment.id,
        )

        # Return the created comment.
        return comment

# ** event: list_section_comments
class ListSectionComments(CommentEvent):
    '''
    Event to list the notes on one section as a flat list.

    Each item carries its own parent id. The server does not build a tree.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document_id', 'section_id'])
    def execute(self,
            document_id: str,
            section_id: str,
            **kwargs,
        ) -> List[SectionComment]:
        '''
        List comments on a section.

        :param document_id: The document identifier.
        :type document_id: str
        :param section_id: The section identifier.
        :type section_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The section's comments, ordered by stored created_at then id.
        :rtype: List[SectionComment]
        '''

        # A missing document or section is an error, not an empty list.
        self._require_section(document_id, section_id)

        # Return the flat list. Ordering is the repository's stored-string sort.
        return self.document_service.list_comments(section_id)

# ** event: remove_section_comment
class RemoveSectionComment(CommentEvent):
    '''
    Event to remove one section comment.

    An unknown id is returned without error. A comment that still has a
    reply is refused, and neither row is deleted. Section delete and
    document delete do not use this refusal.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a section comment by id.

        :param id: The comment identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The comment identifier.
        :rtype: str
        '''

        # False means a reply still names this id and nothing was deleted.
        outcome = self.document_service.delete_comment(id)
        self.verify(
            expression=outcome is not False,
            error_code=a.errors.KB_SECTION_COMMENT_HAS_REPLIES_ID,
            message=f'Section comment {id} still has replies.',
            id=id,
        )

        # An unknown id and a deleted id both return the id.
        return id
