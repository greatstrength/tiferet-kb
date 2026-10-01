"""tiferet_kb Document Link Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
import tables
from pydantic import Field

# ** app
from tiferet.mappers import Aggregate
from tiferet_h5.mappers import TableObject

from ..domain.document_link import DocumentLink
from .document import DocumentTableObject

# *** mappers

# ** mapper: document_link_aggregate
class DocumentLinkAggregate(DocumentLink, Aggregate):
    '''
    The mutable form of a document-to-document link.

    Add stores this shape. There is no update command: a type change is
    remove, then add, and the add is a new link.
    '''

# ** mapper: document_link_table_object
class DocumentLinkTableObject(TableObject):
    '''
    An HDF5 table-row representation of a document link.

    Rows are the sibling of the document header table, in the documents
    group that table uses. Column widths follow that header: identifier
    width for the three identifiers, title width for the type, and
    timestamp width for ``created_at``.
    '''

    # * attribute: id
    id: str = Field(default='', description='Link UUID.')

    # * attribute: source_id
    source_id: str = Field(default='', description='Source document identifier.')

    # * attribute: target_id
    target_id: str = Field(default='', description='Target document identifier.')

    # * attribute: link_type
    link_type: str = Field(default='', description='Stored link type, already stripped.')

    # * attribute: created_at
    created_at: str = Field(default='', description='ISO 8601 creation timestamp.')

    # * attribute: _H5_TYPES
    _H5_TYPES: ClassVar[Dict[str, Any]] = {
        'id': tables.StringCol(DocumentTableObject._H5_TYPES['id'].itemsize),
        'source_id': tables.StringCol(DocumentTableObject._H5_TYPES['id'].itemsize),
        'target_id': tables.StringCol(DocumentTableObject._H5_TYPES['id'].itemsize),
        'link_type': tables.StringCol(DocumentTableObject._H5_TYPES['title'].itemsize),
        'created_at': tables.StringCol(DocumentTableObject._H5_TYPES['created_at'].itemsize),
    }

    # * method: identifier_width
    @classmethod
    def identifier_width(cls) -> int:
        '''
        Return the identifier column width, taken from the header table.

        :return: The byte width of an identifier column.
        :rtype: int
        '''

        # Follow the aligned header id column. Do not invent a width.
        return cls._H5_TYPES['id'].itemsize

    # * method: type_width
    @classmethod
    def type_width(cls) -> int:
        '''
        Return the link-type column width, taken from the header title column.

        :return: The byte width of the link type column.
        :rtype: int
        '''

        # Follow the aligned header title column. Do not invent a width.
        return cls._H5_TYPES['link_type'].itemsize

    # * method: value_fits
    @staticmethod
    def value_fits(value: str, width: int) -> bool:
        '''
        Return whether a string can be stored in a column without clipping.

        A null byte would be cut by a ``StringCol`` even when the byte
        length fits, so it does not fit.

        :param value: The candidate string.
        :type value: str
        :param width: The column width in bytes.
        :type width: int
        :return: True when the encoded value fits in full.
        :rtype: bool
        '''

        # Reject a non-string, a null byte, or a value longer than the column.
        if not isinstance(value, str):
            return False
        encoded = value.encode('utf-8')
        return b'\x00' not in encoded and len(encoded) <= width

    # * method: map
    def map(self, **overrides) -> DocumentLinkAggregate:
        '''
        Map the table row to a document link aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new document link aggregate.
        :rtype: DocumentLinkAggregate
        '''

        # Serialize and construct the aggregate.
        data = self.to_primitive()
        data.update(overrides)
        return DocumentLinkAggregate(**data)

    # * method: from_model
    @classmethod
    def from_model(cls, link: DocumentLink, **overrides) -> 'DocumentLinkTableObject':
        '''
        Create a table object from a document link.

        :param link: The document link to copy from.
        :type link: DocumentLink
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new table object.
        :rtype: DocumentLinkTableObject
        '''

        # Dump the model and apply overrides.
        data = link.model_dump(by_alias=False, exclude_none=True)
        data.update(overrides)
        return cls.model_validate(data)
