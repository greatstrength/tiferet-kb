"""tiferet_kb Embedding Mapper Tests"""

# *** imports

# ** app
from ..embedding import EmbeddingRecordAggregate
from .settings import AggregateTestBase

# *** constants

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = {
    'section_id': 'sec-001',
    'model_name': 'text-embedding-3-small',
    'dimensions': 1536,
    'created_at': '2026-01-01T00:00:00+00:00',
}

# ** constant: equality_fields
EQUALITY_FIELDS = ['section_id', 'model_name', 'dimensions', 'created_at']

# *** classes

# ** class: TestEmbeddingRecordAggregate
class TestEmbeddingRecordAggregate(AggregateTestBase):
    '''Tests for EmbeddingRecordAggregate.'''

    aggregate_cls = EmbeddingRecordAggregate
    sample_data = AGGREGATE_SAMPLE_DATA
    equality_fields = EQUALITY_FIELDS

    set_attribute_params = [
        ('model_name',    'text-embedding-3-large', None),
        ('dimensions',    768,                       None),
        ('invalid_attr',  'value',                   'INVALID_MODEL_ATTRIBUTE'),
    ]
