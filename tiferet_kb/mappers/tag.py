"""tiferet_kb Tag Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
import tables
from pydantic import Field

# ** app
from tiferet.mappers import Aggregate
from tiferet_h5.mappers import NodeObject, TableObject

from ..domain.tag import Tag

# *** mappers

# ** mapper: tag_aggregate
class TagAggregate(Tag, Aggregate):
    '''
    A mutable aggregate representation of a knowledge base tag.

    Mutation stays on the label: rename, or set and clear color. The id is
    not a mutation target because associations key off it.
    '''

    # * method: rename
    def rename(self, name: str) -> None:
        '''
        Rename the tag.

        :param name: The new tag name.
        :type name: str
        :return: None
        :rtype: None
        '''

        # Update the name; validate_assignment=True handles re-validation.
        self.name = name

    # * method: set_color
    def set_color(self, color: str | None) -> None:
        '''
        Set the tag color.

        :param color: The new color string, or None to clear.
        :type color: str | None
        :return: None
        :rtype: None
        '''

        # Update the color.
        self.color = color

# ** mapper: tag_node_object
class TagNodeObject(Tag, NodeObject):
    '''
    An HDF5 node-attribute representation of a knowledge base tag.

    Tag metadata is stored as attributes on a group. The identifier is the
    group name and is not an attribute. Color uses the empty-string sentinel
    so a cleared color does not leave the previous value in place.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_h5.attrs': {'by_alias': True, 'exclude': {'id'}},
    }

    # * attribute: _NULLABLE_FIELDS
    _NULLABLE_FIELDS: ClassVar[list] = ['color']

    # * method: map
    def map(self, **overrides) -> TagAggregate:
        '''
        Map the node object data to a tag aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new tag aggregate.
        :rtype: TagAggregate
        '''

        # Map to the tag aggregate.
        return super().map(TagAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, tag: Tag, **overrides) -> 'TagNodeObject':
        '''
        Create a TagNodeObject from a Tag model.

        :param tag: The tag model to copy from.
        :type tag: Tag
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new TagNodeObject.
        :rtype: TagNodeObject
        '''

        # Create a new TagNodeObject from the model.
        return super().from_model(tag, **overrides)

# ** mapper: document_tag_table_object
class DocumentTagTableObject(TableObject):
    '''
    One row in the document–tag association table.

    This is not a document header column and not a field on ``Document``.
    A row means that document carries that tag. Repeating the pair is the
    repository's job to refuse, not a second row.
    '''

    # * attribute: document_id
    document_id: str = Field(default='', description='Document identifier.')

    # * attribute: tag_id
    tag_id: str = Field(default='', description='Tag identifier.')

    # * attribute: _H5_TYPES
    _H5_TYPES: ClassVar[Dict[str, Any]] = {
        'document_id': tables.StringCol(256),
        'tag_id': tables.StringCol(256),
    }
