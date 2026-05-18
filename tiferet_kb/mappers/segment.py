"""tiferet_kb Segment Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
import tables
from pydantic import Field

# ** app
from tiferet_h5.mappers import TableObject

from ..domain.segment import TextSegment

# *** mappers

# ** mapper: hybrid_segment_table_object
class HybridSegmentTableObject(TableObject):
    '''
    HDF5 table-row representation of a text segment with denormalized
    paragraph metadata.

    Used by the hybrid storage approach: sections are group nodes, but all
    paragraphs and segments live in a single flat table per section. Paragraph
    identity and block type are denormalized onto every segment row.
    '''

    # * attribute: paragraph_id
    paragraph_id: str = Field(default='', description='Parent paragraph UUID.')

    # * attribute: paragraph_position
    paragraph_position: int = Field(default=0, description='Paragraph ordering position.')

    # * attribute: block_type
    block_type: str = Field(default='normal', description='Paragraph block style.')

    # * attribute: id
    id: str = Field(default='', description='Segment UUID.')

    # * attribute: position
    position: int = Field(default=0, description='Segment ordering position within paragraph.')

    # * attribute: text
    text: str = Field(default='', description='Segment text content.')

    # * attribute: format_type
    format_type: str = Field(default='plain', description='Formatting style.')

    # * attribute: link_url
    link_url: str = Field(default='', description='URL for link segments.')

    # * attribute: _H5_TYPES
    _H5_TYPES: ClassVar[Dict[str, Any]] = {
        'paragraph_id':       tables.StringCol(64),
        'paragraph_position': tables.Int32Col(),
        'block_type':         tables.StringCol(32),
        'id':                 tables.StringCol(64),
        'position':           tables.Int32Col(),
        'text':               tables.StringCol(8192),
        'format_type':        tables.StringCol(32),
        'link_url':           tables.StringCol(512),
    }

    # * method: map
    def map(self, **overrides) -> TextSegment:
        '''
        Map to a TextSegment domain object.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new TextSegment.
        :rtype: TextSegment
        '''

        # Serialize, clean empty link_url, and construct.
        data = self.to_primitive()
        if data.get('link_url') == '':
            data['link_url'] = None

        # Remove paragraph-level fields (not part of TextSegment).
        data.pop('paragraph_id', None)
        data.pop('paragraph_position', None)
        data.pop('block_type', None)

        data.update(overrides)
        return TextSegment(**data)
