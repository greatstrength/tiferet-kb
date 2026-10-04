"""tiferet_kb Keyword Index Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
import tables
from pydantic import Field

# ** app
from tiferet_h5.mappers import TableObject

from .document import DocumentTableObject
from .segment import HybridSegmentTableObject

# *** mappers

# ** mapper: keyword_posting_table_object
class KeywordPostingTableObject(TableObject):
    '''
    One inverted-index posting for a term in a section.

    Rows sit beside the document header, not inside the section group, so a
    section delete that has no document id can still drop the term. The term
    column is as wide as segment text, so a token is not clipped to a shorter
    field. Placement is not stored here.
    '''

    # * attribute: term
    term: str = Field(default='', description='Casefolded alphanumeric token.')

    # * attribute: section_id
    section_id: str = Field(default='', description='Indexed section identifier.')

    # * attribute: tf
    tf: int = Field(default=0, description='Term frequency in the rendered body.')

    # * attribute: _H5_TYPES
    _H5_TYPES: ClassVar[Dict[str, Any]] = {
        'term': tables.StringCol(HybridSegmentTableObject._H5_TYPES['text'].itemsize),
        'section_id': tables.StringCol(DocumentTableObject._H5_TYPES['id'].itemsize),
        'tf': tables.Int32Col(),
    }

# ** mapper: keyword_stats_table_object
class KeywordStatsTableObject(TableObject):
    '''
    Token-count statistics for one indexed section.

    ``length`` counts every token, including duplicates, and is at least 1.
    A section with no tokens has no row. ``N`` is the number of these rows.
    '''

    # * attribute: section_id
    section_id: str = Field(default='', description='Indexed section identifier.')

    # * attribute: length
    length: int = Field(default=0, description='Token count of the rendered body.')

    # * attribute: _H5_TYPES
    _H5_TYPES: ClassVar[Dict[str, Any]] = {
        'section_id': tables.StringCol(DocumentTableObject._H5_TYPES['id'].itemsize),
        'length': tables.Int32Col(),
    }
