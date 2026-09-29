"""tiferet_kb Section Comment Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

# ** infra
import tables
from pydantic import Field

# ** app
from tiferet.mappers import Aggregate
from tiferet_h5.mappers import TableObject

from ..domain.comment import (
    AUTHOR_MAX_LENGTH,
    TEXT_MAX_LENGTH,
    SectionComment,
)

# *** mappers

# ** mapper: section_comment_aggregate
class SectionCommentAggregate(SectionComment, Aggregate):
    '''
    A mutable handle for one section comment.

    The note is added or removed as a whole. There is no in-place edit,
    so this aggregate adds no mutation methods.
    '''

# ** mapper: section_comment_table_object
class SectionCommentTableObject(TableObject):
    '''
    An HDF5 table-row representation of a section comment.

    Stored as rows in ``/kb/documents/section_comments``, sibling of the
    document header table. An absent ``parent_id`` is stored as an empty
    string and read back as absent. ``created_at`` is wider than the
    derived 32-character timestamp so a caller-supplied value is not truncated.
    '''

    # * attribute: id
    id: str = Field(default='', description='Comment UUID.')

    # * attribute: document_id
    document_id: str = Field(default='', description='Parent document UUID.')

    # * attribute: section_id
    section_id: str = Field(default='', description='Parent section UUID.')

    # * attribute: author
    author: str = Field(default='', description='Caller-supplied author string.')

    # * attribute: text
    text: str = Field(default='', description='Plain-text note.')

    # * attribute: parent_id
    parent_id: str | None = Field(
        default=None,
        description='Reply parent identifier, absent when this note is not a reply.',
    )

    # * attribute: created_at
    created_at: str = Field(default='', description='ISO 8601 creation timestamp.')

    # * attribute: _H5_TYPES
    _H5_TYPES: ClassVar[Dict[str, Any]] = {
        'id':          tables.StringCol(64),
        'document_id': tables.StringCol(64),
        'section_id':  tables.StringCol(64),
        'author':      tables.StringCol(AUTHOR_MAX_LENGTH),
        'text':        tables.StringCol(TEXT_MAX_LENGTH),
        'parent_id':   tables.StringCol(64),
        'created_at':  tables.StringCol(64),
    }

    # * attribute: _NULLABLE_FIELDS
    _NULLABLE_FIELDS: ClassVar[List[str]] = [
        'parent_id',
    ]

    # * method: map
    def map(self, **overrides) -> SectionCommentAggregate:
        '''
        Map the table row to a section comment aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new section comment aggregate.
        :rtype: SectionCommentAggregate
        '''

        # Serialize, restoring an empty parent id to absent, and construct.
        data = self.to_primitive()
        data.update(overrides)
        return SectionCommentAggregate(**data)

    # * method: from_model
    @classmethod
    def from_model(cls, comment: SectionComment, **overrides) -> 'SectionCommentTableObject':
        '''
        Create a table object from a section comment.

        :param comment: The section comment to copy from.
        :type comment: SectionComment
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new section comment table object.
        :rtype: SectionCommentTableObject
        '''

        # Delegate to the base, which stores an absent parent id as the empty sentinel.
        return super().from_model(comment, **overrides)
