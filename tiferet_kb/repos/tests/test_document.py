"""tiferet_kb Document H5 Repository Integration Tests"""

# *** imports

# ** core
import inspect
import os
from datetime import datetime

# ** infra
import pytest
import tables
from tiferet.assets import TiferetError
from tiferet.events import DomainEvent
from tiferet.interfaces import ServiceError
from tiferet_h5.repos import NodeRepository, TableRepository
from tiferet_h5.utils import H5Client

# ** app
from ...mappers.comment import SectionCommentAggregate
from ...mappers.document import (
    DocumentAggregate,
    DocumentSectionAggregate,
    DocumentTableObject,
)
from ...mappers.segment import HybridSegmentTableObject
from ...events.document import (
    AddDocumentSection,
    ListDocumentSectionRevisions,
    RestoreDocumentSectionRevision,
    UpdateDocumentSection,
)
from ...utils.markdown import parse_content_to_paragraphs
from ..document import (
    DOCUMENTS_TABLE,
    EMBEDDINGS_ARRAY,
    EMBEDDING_IDS_ARRAY,
    SECTION_COMMENTS_TABLE,

    REVISIONS_GROUP_NAME,
    DocumentH5Repository,
)

# *** fixtures

# ** fixture: h5_file
@pytest.fixture
def h5_file(tmp_path) -> str:
    '''Provide a temporary HDF5 file path.'''
    return str(tmp_path / 'test_kb.h5')

# ** fixture: doc_repo
@pytest.fixture
def doc_repo(h5_file: str) -> DocumentH5Repository:
    '''Provide a DocumentH5Repository backed by a temporary HDF5 file.'''
    return DocumentH5Repository(h5_file=h5_file)

# ** fixture: sample_document
@pytest.fixture
def sample_document() -> DocumentAggregate:
    '''Provide a sample DocumentAggregate.'''
    return DocumentAggregate(
        id='doc-001',
        title='Test Document',
        category_id='meeting-notes',
        status='draft',
        created_at='2026-01-01T00:00:00+00:00',
        updated_at='2026-01-01T00:00:00+00:00',
    )

# ** fixture: sample_section
@pytest.fixture
def sample_section() -> DocumentSectionAggregate:
    '''Provide a sample DocumentSectionAggregate.'''
    return DocumentSectionAggregate(
        id='sec-001',
        document_id='doc-001',
        title='Introduction',
        content_type='markdown',
        position=0,
        created_at='2026-01-01T00:00:00+00:00',
        updated_at='2026-01-01T00:00:00+00:00',
    )

# *** tests

# ** test_int: save_and_exists
def test_int_save_and_exists(doc_repo, sample_document):
    '''Test that saving a document makes it exist.'''

    doc_repo.save(sample_document)
    assert doc_repo.exists('doc-001') is True

# ** test_int: exists_negative
def test_int_exists_negative(doc_repo, sample_document):
    '''Test that exists returns False for a non-existent document.'''

    doc_repo.save(sample_document)
    assert doc_repo.exists('nonexistent') is False

# ** test_int: get_success
def test_int_get_success(doc_repo, sample_document):
    '''Test successful retrieval of a saved document.'''

    doc_repo.save(sample_document)
    result = doc_repo.get('doc-001')

    assert result is not None
    assert result.id == 'doc-001'
    assert result.title == 'Test Document'
    assert result.category_id == 'meeting-notes'
    assert result.status == 'draft'

# ** test_int: get_with_sections
def test_int_get_with_sections(doc_repo, sample_document, sample_section):
    '''Test that get() returns document with sections populated.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)

    result = doc_repo.get('doc-001')
    assert result is not None
    assert len(result.sections) == 1
    assert result.sections[0].title == 'Introduction'

# ** test_int: get_not_found
def test_int_get_not_found(doc_repo, sample_document):
    '''Test that get returns None for a non-existent document.'''

    doc_repo.save(sample_document)
    assert doc_repo.get('nonexistent') is None

# ** test_int: list_all
def test_int_list_all(doc_repo):
    '''Test listing all documents.'''

    doc_repo.save(DocumentAggregate(id='doc-001', title='Doc 1', status='draft'))
    doc_repo.save(DocumentAggregate(id='doc-002', title='Doc 2', status='published'))

    result = doc_repo.list()
    assert len(result) == 2

# ** test_int: list_by_status
def test_int_list_by_status(doc_repo):
    '''Test listing documents filtered by status.'''

    doc_repo.save(DocumentAggregate(id='doc-001', title='Doc 1', status='draft'))
    doc_repo.save(DocumentAggregate(id='doc-002', title='Doc 2', status='published'))

    result = doc_repo.list(status='draft')
    assert len(result) == 1
    assert result[0].id == 'doc-001'

# ** test_int: list_empty
def test_int_list_empty(doc_repo):
    '''Test listing when no documents exist.'''

    result = doc_repo.list()
    assert result == []

# ** test_int: list_include_sections
def test_int_list_include_sections(doc_repo):
    '''Test that list(include_sections=True) returns documents with sections populated.'''

    doc_repo.save(DocumentAggregate(id='doc-001', title='Doc 1', status='draft'))
    doc_repo.save(DocumentAggregate(id='doc-002', title='Doc 2', status='published'))

    sec1 = DocumentSectionAggregate(
        id='sec-001', document_id='doc-001', title='Intro',
        content_type='text', position=0,
    )
    sec2 = DocumentSectionAggregate(
        id='sec-002', document_id='doc-001', title='Body',
        content_type='markdown', position=1,
    )
    sec3 = DocumentSectionAggregate(
        id='sec-003', document_id='doc-002', title='Summary',
        content_type='text', position=0,
    )
    doc_repo.save_section(sec1)
    doc_repo.save_section(sec2)
    doc_repo.save_section(sec3)

    result = doc_repo.list(include_sections=True)
    assert len(result) == 2

    # Find each document and verify sections.
    docs_by_id = {d.id: d for d in result}
    assert len(docs_by_id['doc-001'].sections) == 2
    assert docs_by_id['doc-001'].sections[0].position == 0
    assert docs_by_id['doc-001'].sections[1].position == 1
    assert len(docs_by_id['doc-002'].sections) == 1
    assert docs_by_id['doc-002'].sections[0].title == 'Summary'

# ** test_int: list_default_no_sections
def test_int_list_default_no_sections(doc_repo):
    '''Test that list() without include_sections returns documents without sections.'''

    doc_repo.save(DocumentAggregate(id='doc-001', title='Doc 1', status='draft'))
    sec1 = DocumentSectionAggregate(
        id='sec-001', document_id='doc-001', title='Intro',
        content_type='text', position=0,
    )
    doc_repo.save_section(sec1)

    result = doc_repo.list()
    assert len(result) == 1
    assert result[0].sections == []

# ** test_int: save_upsert
def test_int_save_upsert(doc_repo, sample_document):
    '''Test that saving an existing document updates it.'''

    doc_repo.save(sample_document)
    sample_document.rename('Updated Title')
    doc_repo.save(sample_document)

    result = doc_repo.get('doc-001')
    assert result.title == 'Updated Title'

    # Verify no duplicates.
    all_docs = doc_repo.list()
    assert len(all_docs) == 1

# ** test_int: delete_cascades_sections
def test_int_delete_cascades_sections(doc_repo, sample_document, sample_section):
    '''Test that deleting a document cascades to its sections.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)

    doc_repo.delete('doc-001')

    assert doc_repo.exists('doc-001') is False
    assert doc_repo.get_sections('doc-001') == []

# ** test_int: delete_idempotent
def test_int_delete_idempotent(doc_repo, sample_document):
    '''Test that deleting a non-existent document is idempotent.'''

    doc_repo.save(sample_document)
    doc_repo.delete('nonexistent')  # Should not raise.

# ** test_int: save_section_and_get_sections
def test_int_save_section_and_get_sections(doc_repo, sample_document):
    '''Test saving and retrieving sections.'''

    doc_repo.save(sample_document)

    sec1 = DocumentSectionAggregate(
        id='sec-001', document_id='doc-001', title='Intro',
        content_type='text', position=0,
    )
    sec2 = DocumentSectionAggregate(
        id='sec-002', document_id='doc-001', title='Body',
        content_type='markdown', position=1,
    )
    doc_repo.save_section(sec1)
    doc_repo.save_section(sec2)

    sections = doc_repo.get_sections('doc-001')
    assert len(sections) == 2
    assert sections[0].position == 0
    assert sections[1].position == 1

# ** test_int: save_section_upsert
def test_int_save_section_upsert(doc_repo, sample_document, sample_section):
    '''Test that save_section upserts an existing section.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)

    sample_section.rename('Updated Title')
    doc_repo.save_section(sample_section)

    sections = doc_repo.get_sections('doc-001')
    assert len(sections) == 1
    assert sections[0].title == 'Updated Title'

# ** test_int: delete_section
def test_int_delete_section(doc_repo, sample_document, sample_section):
    '''Test deleting a single section.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)

    doc_repo.delete_section('sec-001')
    assert doc_repo.get_sections('doc-001') == []

# ** test_int: reorder_sections
def test_int_reorder_sections(doc_repo, sample_document):
    '''Test reordering sections within a document.'''

    doc_repo.save(sample_document)

    sec1 = DocumentSectionAggregate(
        id='sec-001', document_id='doc-001', title='First',
        content_type='text', position=0,
    )
    sec2 = DocumentSectionAggregate(
        id='sec-002', document_id='doc-001', title='Second',
        content_type='text', position=1,
    )
    doc_repo.save_section(sec1)
    doc_repo.save_section(sec2)

    # Reverse the order.
    doc_repo.reorder_sections('doc-001', ['sec-002', 'sec-001'])

    sections = doc_repo.get_sections('doc-001')
    assert len(sections) == 2
    assert sections[0].id == 'sec-002'
    assert sections[0].position == 0
    assert sections[1].id == 'sec-001'
    assert sections[1].position == 1

# ** test_int: embed_section_and_get_embedding
def test_int_embed_section_and_get_embedding(doc_repo, sample_document, sample_section):
    '''Test embedding storage and retrieval.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)

    embedding = [0.1, 0.2, 0.3, 0.4]
    doc_repo.embed_section('sec-001', embedding, 'test-model')

    result = doc_repo.get_embedding('sec-001')
    assert result is not None
    assert len(result) == 4
    assert abs(result[0] - 0.1) < 1e-5

# ** test_int: get_embedding_not_found
def test_int_get_embedding_not_found(doc_repo):
    '''Test that get_embedding returns None for non-embedded sections.'''

    assert doc_repo.get_embedding('nonexistent') is None

# ** test_int: embed_section_replace
def test_int_embed_section_replace(doc_repo, sample_document, sample_section):
    '''Test that re-embedding a section replaces the previous vector.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)

    doc_repo.embed_section('sec-001', [0.1, 0.2, 0.3], 'test-model')
    doc_repo.embed_section('sec-001', [0.9, 0.8, 0.7], 'test-model')

    result = doc_repo.get_embedding('sec-001')
    assert abs(result[0] - 0.9) < 1e-5

# ** test_int: embed_multiple_sections
def test_int_embed_multiple_sections(doc_repo, sample_document):
    '''Test embedding multiple sections.'''

    doc_repo.save(sample_document)

    sec1 = DocumentSectionAggregate(
        id='sec-001', document_id='doc-001', title='S1',
        content_type='text', position=0,
    )
    sec2 = DocumentSectionAggregate(
        id='sec-002', document_id='doc-001', title='S2',
        content_type='text', position=1,
    )
    doc_repo.save_section(sec1)
    doc_repo.save_section(sec2)

    doc_repo.embed_section('sec-001', [1.0, 0.0, 0.0], 'test-model')
    doc_repo.embed_section('sec-002', [0.0, 1.0, 0.0], 'test-model')

    assert doc_repo.get_embedding('sec-001') is not None
    assert doc_repo.get_embedding('sec-002') is not None

# ** test_int: search_similar
def test_int_search_similar(doc_repo, sample_document):
    '''Test brute-force cosine similarity search.'''

    doc_repo.save(sample_document)

    sec1 = DocumentSectionAggregate(
        id='sec-001', document_id='doc-001', title='S1',
        content_type='text', position=0,
    )
    sec2 = DocumentSectionAggregate(
        id='sec-002', document_id='doc-001', title='S2',
        content_type='text', position=1,
    )
    doc_repo.save_section(sec1)
    doc_repo.save_section(sec2)

    # sec-001 is aligned with query, sec-002 is orthogonal.
    doc_repo.embed_section('sec-001', [1.0, 0.0, 0.0], 'test-model')
    doc_repo.embed_section('sec-002', [0.0, 1.0, 0.0], 'test-model')

    results = doc_repo.search_similar([1.0, 0.0, 0.0], limit=2)
    assert len(results) == 2
    assert results[0]['section_id'] == 'sec-001'
    assert results[0]['score'] > results[1]['score']

# ** test_int: search_similar_empty
def test_int_search_similar_empty(doc_repo):
    '''Test search when no embeddings exist.'''

    results = doc_repo.search_similar([1.0, 0.0, 0.0])
    assert results == []

# ** test_int: remove_embedding
def test_int_remove_embedding(doc_repo, sample_document, sample_section):
    '''Test removing a section's embedding.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)

    doc_repo.embed_section('sec-001', [0.1, 0.2], 'test-model')
    assert doc_repo.get_embedding('sec-001') is not None

    doc_repo.remove_embedding('sec-001')
    assert doc_repo.get_embedding('sec-001') is None

# ** test_int: delete_section_cascades_embedding
def test_int_delete_section_cascades_embedding(doc_repo, sample_document, sample_section):
    '''Test that deleting a section also removes its embedding.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)
    doc_repo.embed_section('sec-001', [0.1, 0.2], 'test-model')

    doc_repo.delete_section('sec-001')
    assert doc_repo.get_embedding('sec-001') is None

# ** test_int: delete_document_cascades_embeddings
def test_int_delete_document_cascades_embeddings(doc_repo, sample_document):
    '''Test that deleting a document removes all section embeddings.'''

    doc_repo.save(sample_document)

    sec1 = DocumentSectionAggregate(
        id='sec-001', document_id='doc-001', title='S1',
        content_type='text', position=0,
    )
    sec2 = DocumentSectionAggregate(
        id='sec-002', document_id='doc-001', title='S2',
        content_type='text', position=1,
    )
    doc_repo.save_section(sec1)
    doc_repo.save_section(sec2)
    doc_repo.embed_section('sec-001', [0.1, 0.2], 'test-model')
    doc_repo.embed_section('sec-002', [0.3, 0.4], 'test-model')

    doc_repo.delete('doc-001')
    assert doc_repo.get_embedding('sec-001') is None
    assert doc_repo.get_embedding('sec-002') is None

# *** tests: RFP-001 storage alignment

# ** test_int: inherits_h5_repository_only
def test_int_inherits_h5_repository_only():
    '''The document repository composes neither storage mixin.'''

    assert not issubclass(DocumentH5Repository, TableRepository)
    assert not issubclass(DocumentH5Repository, NodeRepository)

# ** test_int: header_table_is_stamped
def test_int_header_table_is_stamped(doc_repo, h5_file, sample_document):
    '''The header table carries the fingerprint, and a later save does not rewrite it.'''

    doc_repo.save(sample_document)

    with H5Client(path=h5_file, mode='a') as h5:
        assert h5.get_node_attr(DOCUMENTS_TABLE, 'schema_version') == DocumentTableObject.schema_fingerprint()
        h5.set_node_attr(DOCUMENTS_TABLE, 'schema_version', 'sentinel')

    doc_repo.save(sample_document)

    with H5Client(path=h5_file, mode='r') as h5:
        assert h5.get_node_attr(DOCUMENTS_TABLE, 'schema_version') == 'sentinel'

# ** test_int: segments_table_is_stamped_and_no_document_sections
def test_int_segments_table_is_stamped_and_no_document_sections(doc_repo, h5_file, sample_document, sample_section):
    '''A new section's segments table is stamped; no flat sections table or group stamp exists.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)

    section_path = '/kb/documents/doc-001/sections/sec-001'
    with H5Client(path=h5_file, mode='r') as h5:
        assert h5.get_node_attr(f'{section_path}/segments', 'schema_version') == HybridSegmentTableObject.schema_fingerprint()
        assert not h5.node_exists('/kb/documents/document_sections')
        assert 'schema_version' not in h5.get_node_attrs(section_path)
        assert 'schema_version' not in h5.get_node_attrs('/kb/documents/doc-001')

# ** test_int: save_section_keeps_group_and_replaces_segments
def test_int_save_section_keeps_group_and_replaces_segments(doc_repo, h5_file, sample_document, sample_section):
    '''A second save_section leaves the section group and its other children in place.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)

    # Add a sibling child to the section group and mark the group itself.
    section_path = '/kb/documents/doc-001/sections/sec-001'
    with H5Client(path=h5_file, mode='a') as h5:
        h5.create_group(f'{section_path}/marker')
        h5.set_node_attr(f'{section_path}/marker', 'kept', True)

    # Rewrite the passage with different content.
    sample_section.set_paragraphs(parse_content_to_paragraphs('Rewritten passage.', 'sec-001'))
    doc_repo.save_section(sample_section)

    with H5Client(path=h5_file, mode='r') as h5:
        assert h5.node_exists(f'{section_path}/marker')
        rows = h5.read_rows(f'{section_path}/segments')
        assert len(rows) == 1
        assert rows[0]['text'] == 'Rewritten passage.'
        assert h5.get_node_attr(f'{section_path}/segments', 'schema_version') == HybridSegmentTableObject.schema_fingerprint()

    # Exactly one section remains.
    assert len(doc_repo.get_sections('doc-001')) == 1

# ** test_int: verify_passes_on_fresh_tables
def test_int_verify_passes_on_fresh_tables(doc_repo, sample_document, sample_section):
    '''verify does not raise on tables just created by this code.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)

    doc_repo.verify()
    doc_repo.verify(section_path='/kb/documents/doc-001/sections/sec-001')

# ** test_int: verify_missing_file_or_table_is_noop
def test_int_verify_missing_file_or_table_is_noop(doc_repo, h5_file, sample_document):
    '''verify on a missing file, a missing table, or a missing section does nothing and creates nothing.'''

    doc_repo.verify()
    assert not os.path.exists(h5_file)

    doc_repo.save(sample_document)
    doc_repo.verify(section_path='/kb/documents/doc-001/sections/none')

# ** test_int: verify_raises_on_column_drift
def test_int_verify_raises_on_column_drift(doc_repo, h5_file):
    '''verify raises H5_SCHEMA_MISMATCH when a column width has changed.'''

    # Build the header table with a narrower title column.
    narrow = type(
        'NarrowDocumentDescription',
        (tables.IsDescription,),
        {**DocumentTableObject._H5_TYPES, 'title': tables.StringCol(32)},
    )
    with H5Client(path=h5_file, mode='a') as h5:
        h5.create_table(DOCUMENTS_TABLE, narrow)

    with pytest.raises(ServiceError) as exc_info:
        doc_repo.verify()
    assert exc_info.value.error_code == 'H5_SCHEMA_MISMATCH'

# ** test_int: unstamped_file_still_opens
def test_int_unstamped_file_still_opens(doc_repo, h5_file, sample_document):
    '''A file written without schema_version still lists, verifies, and is not stamped by reads.'''

    # Write the header table the way the prototype did: no stamp.
    with H5Client(path=h5_file, mode='a') as h5:
        t = h5.create_table(DOCUMENTS_TABLE, DocumentTableObject.get_description())
        DocumentTableObject.from_model(sample_document).to_row(t)
        t.flush()

    listed = doc_repo.list()
    assert [d.id for d in listed] == ['doc-001']
    assert doc_repo.get('doc-001') is not None
    assert doc_repo.exists('doc-001') is True
    doc_repo.verify()

    with H5Client(path=h5_file, mode='r') as h5:
        assert 'schema_version' not in h5.get_node_attrs(DOCUMENTS_TABLE)

# ** test_int: embed_dimension_mismatch
def test_int_embed_dimension_mismatch(doc_repo, sample_document, sample_section):
    '''A vector of a different length raises a storage ServiceError, not a catalog code.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)
    doc_repo.embed_section('sec-001', [0.1, 0.2, 0.3], 'test-model')

    with pytest.raises(ServiceError) as exc_info:
        doc_repo.embed_section('sec-002', [0.1, 0.2], 'test-model')
    assert exc_info.value.error_code == 'H5_EMBEDDING_DIMENSION_MISMATCH'

    # The stored embedding is untouched.
    assert doc_repo.get_embedding('sec-001') is not None

# ** test_int: search_similar_signature
def test_int_search_similar_signature():
    '''search_similar keeps folder_id and category_id and accepts document_id.'''

    params = inspect.signature(DocumentH5Repository.search_similar).parameters
    assert 'folder_id' in params
    assert 'category_id' in params
    assert 'document_id' in params
    assert params['document_id'].default is None
    assert 'visibility' not in params
    assert 'owner_id' not in params

# ** test_int: delete_section_scan_preserves_header_and_arrays
def test_int_delete_section_scan_preserves_header_and_arrays(doc_repo, h5_file, sample_document, sample_section):
    '''Deleting a section without a document id leaves the header table and the other arrays alone.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)
    doc_repo.embed_section('sec-001', [0.1, 0.2, 0.3], 'test-model')
    doc_repo.embed_section('sec-keep', [0.3, 0.2, 0.1], 'test-model')

    doc_repo.delete_section('sec-001')

    with H5Client(path=h5_file, mode='r') as h5:
        assert not h5.node_exists('/kb/documents/doc-001/sections/sec-001')
        assert h5.node_exists(DOCUMENTS_TABLE)
        assert h5.node_exists(EMBEDDINGS_ARRAY)
        assert h5.node_exists(EMBEDDING_IDS_ARRAY)

    assert doc_repo.exists('doc-001') is True
    assert doc_repo.get_embedding('sec-001') is None
    assert doc_repo.get_embedding('sec-keep') is not None

# ** test_int: delete_document_missing_is_noop
def test_int_delete_document_missing_is_noop(doc_repo, sample_document):
    '''Deleting an absent document does not raise.'''

    doc_repo.save(sample_document)
    doc_repo.delete('nonexistent')

# *** tests: RFP-009 agent substrate

# ** test_int: content_round_trip_does_not_store_content
def test_int_content_round_trip_does_not_store_content(doc_repo, h5_file):
    '''A content string round-trips through paragraphs and is not a group attribute.'''

    doc_repo.save(DocumentAggregate(id='ns-1', title='memory:agent:default'))
    section = DocumentSectionAggregate(
        id='fact-1',
        document_id='ns-1',
        title='user prefers',
        content='user prefers Python',
    )
    doc_repo.save_section(section)

    loaded = doc_repo.get_sections('ns-1')
    assert len(loaded) == 1
    assert loaded[0].content == 'user prefers Python'

    section_path = '/kb/documents/ns-1/sections/fact-1'
    with H5Client(path=h5_file, mode='r') as h5:
        assert 'content' not in h5.get_node_attrs(section_path)
        rows = h5.read_rows(f'{section_path}/segments')
        assert rows[0]['text'] == 'user prefers Python'

# ** test_int: list_title_is_exact_header_equality
def test_int_list_title_is_exact_header_equality(doc_repo):
    '''Title is exact, case-sensitive, and conjunctive. Empty title adds no condition.'''

    doc_repo.save(DocumentAggregate(
        id='ns-1', title='memory:agent:default', folder_id='folder-1',
        category_id='notes', status='draft',
    ))
    doc_repo.save(DocumentAggregate(
        id='ns-2', title='memory:agent:default', folder_id='folder-2',
        category_id='notes', status='published',
    ))
    doc_repo.save(DocumentAggregate(
        id='other', title='Memory:agent:default', folder_id='folder-1',
        category_id='notes', status='draft',
    ))
    doc_repo.save_section(DocumentSectionAggregate(
        id='sec-other', document_id='other', title='Not loaded', position=0,
    ))

    assert {d.id for d in doc_repo.list()} == {'ns-1', 'ns-2', 'other'}
    assert {d.id for d in doc_repo.list(title='')} == {'ns-1', 'ns-2', 'other'}
    matched = doc_repo.list(title='memory:agent:default', include_sections=True)
    assert {d.id for d in matched} == {'ns-1', 'ns-2'}
    assert all(d.sections == [] for d in matched)

    conjunct = doc_repo.list(
        title='memory:agent:default',
        folder_id='folder-1',
        category_id='notes',
        status='draft',
    )
    assert [d.id for d in conjunct] == ['ns-1']

# ** test_int: list_title_escapes_colon_and_quote
def test_int_list_title_escapes_colon_and_quote(doc_repo, monkeypatch):
    '''A colon title and a quote title match only themselves and do not scan the file.'''

    colon = 'memory:agent:default'
    quoted = 'say "hi"'
    doc_repo.save(DocumentAggregate(id='colon', title=colon))
    doc_repo.save(DocumentAggregate(id='quoted', title=quoted))
    doc_repo.save(DocumentAggregate(id='other', title='other title'))

    read_calls = []
    original = H5Client.read_rows

    def spy_read(self, path, start=None, stop=None, condition=None):
        read_calls.append(condition)
        return original(self, path, start=start, stop=stop, condition=condition)

    monkeypatch.setattr(H5Client, 'read_rows', spy_read)

    assert [d.id for d in doc_repo.list(title=colon)] == ['colon']
    assert [d.id for d in doc_repo.list(title=quoted)] == ['quoted']
    assert read_calls == []

# ** test_int: search_similar_document_id_masks_before_limit
def test_int_search_similar_document_id_masks_before_limit(doc_repo, monkeypatch):
    '''document_id restricts candidates before limit and does not scan headers when alone.'''

    doc_repo.save(DocumentAggregate(id='wide', title='Wide', folder_id='folder-1', category_id='notes'))
    doc_repo.save(DocumentAggregate(id='ns-1', title='Namespace', folder_id='folder-1', category_id='notes'))
    doc_repo.save_section(DocumentSectionAggregate(id='wide-1', document_id='wide', title='W', position=0))
    doc_repo.save_section(DocumentSectionAggregate(id='ns-sec', document_id='ns-1', title='N', position=0))
    doc_repo.embed_section('wide-1', [1.0, 0.0, 0.0], 'test-model')
    doc_repo.embed_section('ns-sec', [0.2, 0.9, 0.0], 'test-model')

    header_reads = []
    original = H5Client.read_rows

    def spy_read(self, path, start=None, stop=None, condition=None):
        if path == DOCUMENTS_TABLE:
            header_reads.append(condition)
        return original(self, path, start=start, stop=stop, condition=condition)

    monkeypatch.setattr(H5Client, 'read_rows', spy_read)

    file_wide = doc_repo.search_similar([1.0, 0.0, 0.0], limit=1)
    assert file_wide[0]['section_id'] == 'wide-1'

    scoped = doc_repo.search_similar([1.0, 0.0, 0.0], limit=1, document_id='ns-1')
    assert [hit['section_id'] for hit in scoped] == ['ns-sec']
    assert header_reads == []

    assert doc_repo.search_similar([1.0, 0.0, 0.0], document_id='missing') == []
    both = doc_repo.search_similar(
        [1.0, 0.0, 0.0],
        document_id='ns-1',
        folder_id='folder-1',
        category_id='notes',
    )
    assert [hit['section_id'] for hit in both] == ['ns-sec']
    mismatch = doc_repo.search_similar(
        [1.0, 0.0, 0.0],
        document_id='ns-1',
        folder_id='other-folder',
    )
    assert mismatch == []

# *** tests: RFP-008 visibility

# ** test_int: save_get_visibility_and_owner
def test_int_save_get_visibility_and_owner(doc_repo):
    '''A document can store visibility and an optional owner, and get returns them.'''

    doc_repo.save(DocumentAggregate(
        id='doc-private',
        title='Private Doc',
        status='published',
        visibility='private',
        owner_id='owner-1',
    ))

    loaded = doc_repo.get('doc-private')
    assert loaded.visibility == 'private'
    assert loaded.owner_id == 'owner-1'
    assert loaded.visibility is not None

# ** test_int: list_visibility_and_owner_conjoin
def test_int_list_visibility_and_owner_conjoin(doc_repo):
    '''Visibility and owner filters conjoin with status, and an omitted filter hides nothing.'''

    doc_repo.save(DocumentAggregate(id='doc-pub', title='Pub', status='draft', visibility='public'))
    doc_repo.save(DocumentAggregate(
        id='doc-priv', title='Priv', status='draft', visibility='private', owner_id='owner-1',
    ))
    doc_repo.save(DocumentAggregate(
        id='doc-arch', title='Arch', status='archived', visibility='private', owner_id='owner-1',
    ))

    # Omitted filters do not hide private rows, and get needs no caller.
    assert {d.id for d in doc_repo.list()} == {'doc-pub', 'doc-priv', 'doc-arch'}
    assert doc_repo.get('doc-priv').visibility == 'private'

    # public includes the stored public row. private does not include it.
    assert {d.id for d in doc_repo.list(visibility='public')} == {'doc-pub'}
    assert {d.id for d in doc_repo.list(visibility='private', status='draft')} == {'doc-priv'}
    assert {d.id for d in doc_repo.list(owner_id='owner-1', status='draft')} == {'doc-priv'}
    assert doc_repo.list(owner_id='missing') == []

# ** test_int: list_public_includes_empty_visibility
def test_int_list_public_includes_empty_visibility(doc_repo, h5_file):
    '''visibility=public includes a stored empty visibility. private does not.'''

    doc_repo.save(DocumentAggregate(id='doc-empty', title='Empty', status='draft'))
    with H5Client(path=h5_file, mode='a') as h5:
        h5.remove_rows(DOCUMENTS_TABLE, '(id == b"doc-empty")')
        table = h5.get_table(DOCUMENTS_TABLE)
        DocumentTableObject(
            id='doc-empty', title='Empty', status='draft', visibility='', owner_id='',
            created_at='2026-01-01T00:00:00+00:00', updated_at='2026-01-01T00:00:00+00:00',
        ).to_row(table)
        table.flush()

    loaded = doc_repo.get('doc-empty')
    assert loaded.visibility == 'public'
    assert loaded.owner_id is None
    assert [d.id for d in doc_repo.list(visibility='public')] == ['doc-empty']
    assert doc_repo.list(visibility='restricted') == []
    assert doc_repo.list(owner_id='owner-1') == []

# ** test_int: prechange_document_reads_public_without_rewrite
def test_int_prechange_document_reads_public_without_rewrite(doc_repo, h5_file):
    '''A header written before these columns exist reads as public with no owner.'''

    # Build the header table without visibility or owner_id.
    old_types = {
        'id': tables.StringCol(64),
        'title': tables.StringCol(512),
        'category_id': tables.StringCol(64),
        'template_id': tables.StringCol(64),
        'folder_id': tables.StringCol(64),
        'status': tables.StringCol(32),
        'created_at': tables.StringCol(32),
        'updated_at': tables.StringCol(32),
    }
    description = type('OldDocumentDescription', (tables.IsDescription,), old_types)
    with tables.open_file(h5_file, mode='w') as h5file:
        table = h5file.create_table('/kb/documents', 'documents', description, createparents=True)
        row = table.row
        row['id'] = b'doc-old'
        row['title'] = b'Old Document'
        row['category_id'] = b''
        row['template_id'] = b''
        row['folder_id'] = b''
        row['status'] = b'draft'
        row['created_at'] = b'2026-01-01T00:00:00+00:00'
        row['updated_at'] = b'2026-01-01T00:00:00+00:00'
        row.append()
        table.flush()

    loaded = doc_repo.get('doc-old')
    assert loaded is not None
    assert loaded.visibility == 'public'
    assert loaded.owner_id is None
    assert loaded.title == 'Old Document'

    # public includes the absent column. private and an owner filter do not.
    assert [d.id for d in doc_repo.list(visibility='public')] == ['doc-old']
    assert doc_repo.list(visibility='private') == []
    assert doc_repo.list(visibility='restricted') == []
    assert doc_repo.list(owner_id='owner-1') == []
    assert [d.id for d in doc_repo.list()] == ['doc-old']

    # Reading did not add the columns.
    with H5Client(path=h5_file, mode='r') as h5:
        assert 'visibility' not in h5.get_table(DOCUMENTS_TABLE).colnames
        assert 'owner_id' not in h5.get_table(DOCUMENTS_TABLE).colnames

# ** test_int: list_rejects_unknown_visibility
def test_int_list_rejects_unknown_visibility(doc_repo):
    '''An unrecognized visibility filter is KB_INVALID_VISIBILITY, not an empty list.'''

    with pytest.raises(TiferetError) as exc_info:
        doc_repo.list(visibility='draft')
    assert exc_info.value.error_code == 'KB_INVALID_VISIBILITY'
    assert 'status' not in exc_info.value.kwargs.get('message', str(exc_info.value))

# ** test_int: list_comments_missing_file_does_not_create
def test_int_list_comments_missing_file_does_not_create(doc_repo, h5_file):
    '''A comment read on a missing file returns empty and does not create the file.'''

    assert doc_repo.list_comments('sec-001') == []
    assert doc_repo.delete_comment('missing') is None
    assert not os.path.exists(h5_file)

# ** test_int: comments_sort_by_stored_strings
def test_int_comments_sort_by_stored_strings(doc_repo):
    '''List sorts stored created_at then id, and does not nest replies.'''

    doc_repo.add_comment(SectionCommentAggregate(
        id='b-id', document_id='doc-001', section_id='sec-001',
        author='ada', text='later id', created_at='9',
    ))
    doc_repo.add_comment(SectionCommentAggregate(
        id='a-id', document_id='doc-001', section_id='sec-001',
        author='ada', text='same time', created_at='9', parent_id='b-id',
    ))
    doc_repo.add_comment(SectionCommentAggregate(
        id='z-id', document_id='doc-001', section_id='sec-001',
        author='ada', text='string-sorts first', created_at='10',
    ))
    doc_repo.add_comment(SectionCommentAggregate(
        id='other', document_id='doc-001', section_id='sec-002',
        author='ada', text='other section', created_at='1',
    ))

    listed = doc_repo.list_comments('sec-001')
    assert [item.id for item in listed] == ['z-id', 'a-id', 'b-id']
    assert listed[1].parent_id == 'b-id'
    assert 'replies' not in type(listed[1]).model_fields

# ** test_int: duplicate_comment_does_not_replace_text
def test_int_duplicate_comment_does_not_replace_text(doc_repo):
    '''A second insert of the same id leaves the stored text unchanged.'''

    doc_repo.add_comment(SectionCommentAggregate(
        id='cmt-001', document_id='doc-001', section_id='sec-001',
        author='ada', text='original', created_at='2026-01-01T00:00:00+00:00',
    ))
    inserted = doc_repo.add_comment(SectionCommentAggregate(
        id='cmt-001', document_id='doc-001', section_id='sec-001',
        author='ada', text='replacement', created_at='2026-01-02T00:00:00+00:00',
    ))
    assert inserted is False
    assert doc_repo.list_comments('sec-001')[0].text == 'original'

# ** test_int: delete_comment_refuses_while_replies_remain
def test_int_delete_comment_refuses_while_replies_remain(doc_repo):
    '''Removing a parent leaves both rows; removing the reply then the parent deletes each row only.'''

    doc_repo.add_comment(SectionCommentAggregate(
        id='cmt-1', document_id='doc-001', section_id='sec-001',
        author='ada', text='parent', created_at='2026-01-01T00:00:00+00:00',
    ))
    doc_repo.add_comment(SectionCommentAggregate(
        id='cmt-2', document_id='doc-001', section_id='sec-001',
        author='ada', text='reply', parent_id='cmt-1', created_at='2026-01-02T00:00:00+00:00',
    ))

    assert doc_repo.delete_comment('cmt-1') is False
    assert {item.id for item in doc_repo.list_comments('sec-001')} == {'cmt-1', 'cmt-2'}

    assert doc_repo.delete_comment('cmt-2') is True
    assert [item.id for item in doc_repo.list_comments('sec-001')] == ['cmt-1']
    assert doc_repo.delete_comment('cmt-1') is True
    assert doc_repo.list_comments('sec-001') == []
    assert doc_repo.delete_comment('cmt-1') is None

# ** test_int: delete_section_cascades_comments_even_when_group_is_gone
def test_int_delete_section_cascades_comments_even_when_group_is_gone(doc_repo, h5_file):
    '''Section delete removes that section's comments and leaves other sections' comments.'''

    doc_repo.add_comment(SectionCommentAggregate(
        id='gone', document_id='doc-001', section_id='sec-gone',
        author='ada', text='cascade me', created_at='2026-01-01T00:00:00+00:00',
    ))
    doc_repo.add_comment(SectionCommentAggregate(
        id='keep', document_id='doc-001', section_id='sec-keep',
        author='ada', text='stay', created_at='2026-01-01T00:00:00+00:00',
    ))

    doc_repo.delete_section('sec-gone')

    assert doc_repo.list_comments('sec-gone') == []
    assert [item.id for item in doc_repo.list_comments('sec-keep')] == ['keep']
    with H5Client(path=h5_file, mode='r') as h5:
        assert h5.node_exists(SECTION_COMMENTS_TABLE)
        assert not h5.node_exists('/kb/documents/doc-001/sections/sec-gone')

# ** test_int: delete_document_cascades_comments
def test_int_delete_document_cascades_comments(doc_repo):
    '''Document delete removes that document's comments and leaves other documents' comments.'''

    doc_repo.add_comment(SectionCommentAggregate(
        id='mine', document_id='doc-001', section_id='sec-001',
        author='ada', text='mine', created_at='2026-01-01T00:00:00+00:00',
    ))
    doc_repo.add_comment(SectionCommentAggregate(
        id='theirs', document_id='doc-002', section_id='sec-002',
        author='ada', text='theirs', created_at='2026-01-01T00:00:00+00:00',
    ))

    doc_repo.delete('doc-001')

    assert doc_repo.list_comments('sec-001') == []
    assert [item.id for item in doc_repo.list_comments('sec-002')] == ['theirs']

# ** test_int: save_and_reorder_leave_comments
def test_int_save_and_reorder_leave_comments(doc_repo, sample_document, sample_section):
    '''A passage rewrite and a reorder do not change the section's comments.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)
    doc_repo.add_comment(SectionCommentAggregate(
        id='cmt-001', document_id='doc-001', section_id='sec-001',
        author='ada', text='survives rewrite', created_at='2026-01-01T00:00:00+00:00',
    ))

    sample_section.set_paragraphs(parse_content_to_paragraphs('Rewritten passage.', 'sec-001'))
    doc_repo.save_section(sample_section)
    doc_repo.reorder_sections('doc-001', ['sec-001'])

    listed = doc_repo.list_comments('sec-001')
    assert len(listed) == 1
    assert listed[0].text == 'survives rewrite'
    assert doc_repo.get_sections('doc-001')[0].paragraphs[0].segments[0].text == 'Rewritten passage.'

# ** test_int: comment_row_removal_does_not_call_remove_node
def test_int_comment_row_removal_does_not_call_remove_node(doc_repo, h5_file):
    '''Comment row removal uses remove_rows, never remove_node on the comments table.'''

    doc_repo.add_comment(SectionCommentAggregate(
        id='cmt-001', document_id='doc-001', section_id='sec-001',
        author='ada', text='note', created_at='2026-01-01T00:00:00+00:00',
    ))
    removed = []
    original = doc_repo.node_repo.remove_node

    def spy(h5, path, recursive=False):
        removed.append(path)
        return original(h5, path, recursive=recursive)

    doc_repo.node_repo.remove_node = spy
    assert doc_repo.delete_comment('cmt-001') is True
    doc_repo.delete_section('sec-001')
    doc_repo.delete('doc-001')

    assert SECTION_COMMENTS_TABLE not in removed
    comment_source = inspect.getsource(DocumentH5Repository.delete_comment)
    cascade_source = inspect.getsource(DocumentH5Repository._remove_comment_rows)
    assert 'self.node_repo.remove_node' not in comment_source
    assert 'h5.h5file.remove_node' not in comment_source
    assert 'self.node_repo.remove_node' not in cascade_source
    assert 'h5.h5file.remove_node' not in cascade_source
    assert 'remove_rows' in cascade_source
    with H5Client(path=h5_file, mode='r') as h5:
        assert h5.node_exists(SECTION_COMMENTS_TABLE)
        assert not any(row['id'] == 'cmt-001' for row in h5.read_rows(SECTION_COMMENTS_TABLE))

# *** tests: RFP-006 section history

# ** test_int: list_revisions_missing_file
def test_int_list_revisions_missing_file(doc_repo, h5_file):
    '''A missing file lists as empty and is not created.'''

    assert doc_repo.list_section_revisions('doc-001', 'sec-001') == []
    assert doc_repo.get_section_revision('doc-001', 'sec-001', 1) is None
    assert not os.path.exists(h5_file)

# ** test_int: missing_collection_lists_empty
def test_int_missing_collection_lists_empty(doc_repo, h5_file, sample_document, sample_section):
    '''A section written before history lists as empty and is not rewritten.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)

    assert doc_repo.list_section_revisions('doc-001', 'sec-001') == []
    assert len(doc_repo.get_sections('doc-001')) == 1

    with H5Client(path=h5_file, mode='r') as h5:
        assert not h5.node_exists(
            f'/kb/documents/doc-001/sections/sec-001/{REVISIONS_GROUP_NAME}'
        )

# ** test_int: empty_paragraph_snapshot_survives_save
def test_int_empty_paragraph_snapshot_survives_save(doc_repo, h5_file, sample_document, sample_section):
    '''An empty snapshot is a real group, and save_section leaves that group in place.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)
    section_path = '/kb/documents/doc-001/sections/sec-001'

    revision = doc_repo.append_section_revision(
        document_id='doc-001',
        section_id='sec-001',
        title='Introduction',
        content_type='markdown',
        paragraphs=[],
    )

    assert revision.number == 1
    assert revision.paragraphs == []
    assert 'content' not in type(revision).model_fields

    sample_section.set_paragraphs(parse_content_to_paragraphs('Later passage.', 'sec-001'))
    doc_repo.save_section(sample_section)

    with H5Client(path=h5_file, mode='r') as h5:
        revision_path = f'{section_path}/{REVISIONS_GROUP_NAME}/rev_1'
        assert h5.node_exists(section_path)
        assert h5.node_exists(revision_path)
        assert h5.node_exists(f'{revision_path}/segments')
        assert h5.read_rows(f'{revision_path}/segments') == []
        attrs = h5.get_node_attrs(revision_path)
        assert 'content' not in attrs
        assert 'author' not in attrs
        colnames = h5.get_table(f'{revision_path}/segments').colnames
        assert 'content' not in colnames
        assert set(colnames) == set(HybridSegmentTableObject._H5_TYPES)

    listed = doc_repo.list_section_revisions('doc-001', 'sec-001')
    assert [item.number for item in listed] == [1]
    assert listed[0].paragraphs == []
    assert doc_repo.get_sections('doc-001')[0].paragraphs[0].segments[0].text == 'Later passage.'

# ** test_int: history_nests_under_section_and_restore_keeps_embedding
def test_int_history_nests_under_section_and_restore_keeps_embedding(doc_repo, h5_file):
    '''Content updates and restore keep every prior revision under the section group.'''

    doc_repo.save(DocumentAggregate(id='doc-001', title='Doc', status='draft'))
    section = DomainEvent.handle(
        AddDocumentSection,
        dependencies={'document_service': doc_repo},
        document_id='doc-001',
        title='Intro',
        content='Alpha',
        heading_level=3,
        icon='star',
        position=0,
    )
    doc_repo.embed_section(section.id, [0.2, 0.4, 0.6], 'test-model')
    embedding = doc_repo.get_embedding(section.id)
    original_ids = (section.paragraphs[0].id, section.paragraphs[0].segments[0].id)
    section_path = f'/kb/documents/doc-001/sections/{section.id}'

    # An identical content write appends nothing and keeps stored identifiers.
    same = DomainEvent.handle(
        UpdateDocumentSection,
        dependencies={'document_service': doc_repo},
        id=section.id,
        attribute='content',
        value='Alpha',
        document_id='doc-001',
    )
    assert same.paragraphs[0].id == original_ids[0]
    assert doc_repo.list_section_revisions('doc-001', section.id) == []

    # The first content change snapshots the previous passages before replacing them.
    updated = DomainEvent.handle(
        UpdateDocumentSection,
        dependencies={'document_service': doc_repo},
        id=section.id,
        attribute='content',
        value='Beta',
        document_id='doc-001',
    )
    first = doc_repo.list_section_revisions('doc-001', section.id)
    assert [item.number for item in first] == [1]
    assert first[0].title == 'Intro'
    assert first[0].content_type == 'markdown'
    assert first[0].paragraphs[0].id == original_ids[0]
    assert first[0].paragraphs[0].segments[0].id == original_ids[1]
    assert datetime.fromisoformat(first[0].created_at).tzinfo is not None
    assert updated.paragraphs[0].segments[0].text == 'Beta'
    assert updated.paragraphs[0].id != original_ids[0]

    with H5Client(path=h5_file, mode='r') as h5:
        assert h5.node_exists(section_path)
        assert h5.node_exists(f'{section_path}/{REVISIONS_GROUP_NAME}/rev_1')
        children = list(h5.get_group('/kb/documents/doc-001/sections')._v_children.keys())
        assert children == [section.id]

    # A second content change leaves revision 1 readable.
    DomainEvent.handle(
        UpdateDocumentSection,
        dependencies={'document_service': doc_repo},
        id=section.id,
        attribute='content',
        value='Gamma',
        document_id='doc-001',
    )
    assert [item.number for item in doc_repo.list_section_revisions('doc-001', section.id)] == [2, 1]
    assert doc_repo.get_section_revision('doc-001', section.id, 1).paragraphs[0].id == original_ids[0]

    # A heading change is not a revision.
    renamed = DomainEvent.handle(
        UpdateDocumentSection,
        dependencies={'document_service': doc_repo},
        id=section.id,
        attribute='title',
        value='Renamed',
        document_id='doc-001',
    )
    assert renamed.title == 'Renamed'
    assert [item.number for item in doc_repo.list_section_revisions('doc-001', section.id)] == [2, 1]

    # Restore writes the snapshot's identifiers and leaves the heading and vector alone.
    restored = DomainEvent.handle(
        RestoreDocumentSectionRevision,
        dependencies={'document_service': doc_repo},
        id=section.id,
        document_id='doc-001',
        number=1,
    )
    assert restored.title == 'Renamed'
    assert restored.content_type == 'markdown'
    assert restored.heading_level == 3
    assert restored.icon == 'star'
    assert restored.position == 0
    assert restored.paragraphs[0].id == original_ids[0]
    assert restored.paragraphs[0].segments[0].text == 'Alpha'
    assert doc_repo.get_embedding(section.id) == embedding
    listed = DomainEvent.handle(
        ListDocumentSectionRevisions,
        dependencies={'document_service': doc_repo},
        id=section.id,
        document_id='doc-001',
    )
    assert [item.number for item in listed] == [3, 2, 1]
    assert listed[0].title == 'Renamed'
    assert listed[0].paragraphs[0].segments[0].text == 'Gamma'
    assert 'content' not in type(listed[0]).model_fields

    # Restore still appends when the current passages already match the snapshot.
    DomainEvent.handle(
        RestoreDocumentSectionRevision,
        dependencies={'document_service': doc_repo},
        id=section.id,
        document_id='doc-001',
        number=1,
    )
    assert [item.number for item in doc_repo.list_section_revisions('doc-001', section.id)] == [4, 3, 2, 1]
    assert len(doc_repo.get('doc-001').sections) == 1
    assert doc_repo.get('doc-001').sections[0].paragraphs[0].id == original_ids[0]

    # A missing revision does not append.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            RestoreDocumentSectionRevision,
            dependencies={'document_service': doc_repo},
            id=section.id,
            document_id='doc-001',
            number=99,
        )
    assert exc_info.value.error_code == 'KB_SECTION_REVISION_NOT_FOUND'
    assert [item.number for item in doc_repo.list_section_revisions('doc-001', section.id)] == [4, 3, 2, 1]

    # Deleting the section removes the nested revisions with the group.
    doc_repo.delete_section(section.id, document_id='doc-001')
    with H5Client(path=h5_file, mode='r') as h5:
        assert not h5.node_exists(section_path)
        assert not h5.node_exists(f'{section_path}/{REVISIONS_GROUP_NAME}')

# ** test_int: delete_document_removes_revisions
def test_int_delete_document_removes_revisions(doc_repo, h5_file, sample_document, sample_section):
    '''Deleting the document leaves no revision reachable for its section.'''

    doc_repo.save(sample_document)
    doc_repo.save_section(sample_section)
    doc_repo.append_section_revision(
        document_id='doc-001',
        section_id='sec-001',
        title='Introduction',
        content_type='markdown',
        paragraphs=parse_content_to_paragraphs('Kept once.', 'sec-001'),
    )

    doc_repo.delete('doc-001')

    with H5Client(path=h5_file, mode='r') as h5:
        assert not h5.node_exists('/kb/documents/doc-001')
    assert doc_repo.list_section_revisions('doc-001', 'sec-001') == []
