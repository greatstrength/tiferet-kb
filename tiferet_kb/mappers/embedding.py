"""tiferet_kb Embedding Mappers"""

# *** imports

# ** app
from tiferet.mappers import Aggregate

from ..domain.embedding import EmbeddingRecord

# *** mappers

# ** mapper: embedding_record_aggregate
class EmbeddingRecordAggregate(EmbeddingRecord, Aggregate):
    '''
    A mutable aggregate representation of an embedding record.

    No domain-specific mutation methods are needed beyond the inherited
    ``set_attribute`` from ``Aggregate``.
    '''

    pass
