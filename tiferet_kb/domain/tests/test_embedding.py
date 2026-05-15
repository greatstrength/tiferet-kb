"""tiferet_kb Embedding Domain Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..embedding import EmbeddingRecord

# *** tests

# ** test: embedding_record_constructor
def test_embedding_record_constructor():
    '''
    Test EmbeddingRecord construction with all required fields.
    '''

    # Create an embedding record with explicit values.
    record = EmbeddingRecord(
        section_id='abc-123',
        model_name='text-embedding-3-small',
        dimensions=1536,
        created_at='2026-01-01T00:00:00+00:00',
    )

    # Assert all fields are set correctly.
    assert record.section_id == 'abc-123'
    assert record.model_name == 'text-embedding-3-small'
    assert record.dimensions == 1536
    assert record.created_at == '2026-01-01T00:00:00+00:00'


# ** test: embedding_record_defaults
def test_embedding_record_defaults():
    '''
    Test EmbeddingRecord auto-derives created_at when not provided.
    '''

    # Create an embedding record without created_at.
    record = EmbeddingRecord(
        section_id='def-456',
        model_name='text-embedding-3-large',
        dimensions=768,
    )

    # Assert created_at is auto-generated (non-empty ISO string).
    assert record.created_at is not None
    assert len(record.created_at) > 0
    assert 'T' in record.created_at
