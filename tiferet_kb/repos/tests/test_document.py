"""tiferet_kb Document H5 Repository Integration Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...mappers.document import DocumentAggregate, DocumentSectionAggregate
from ..document import DocumentH5Repository

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
        content='# Hello World',
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
    assert result.sections[0].content == '# Hello World'


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
        content_type='text', content='Hello', position=0,
    )
    sec2 = DocumentSectionAggregate(
        id='sec-002', document_id='doc-001', title='Body',
        content_type='markdown', content='## Content', position=1,
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

    sample_section.set_content('Updated content')
    doc_repo.save_section(sample_section)

    sections = doc_repo.get_sections('doc-001')
    assert len(sections) == 1
    assert sections[0].content == 'Updated content'


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
        content_type='text', content='A', position=0,
    )
    sec2 = DocumentSectionAggregate(
        id='sec-002', document_id='doc-001', title='Second',
        content_type='text', content='B', position=1,
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
        content_type='text', content='A', position=0,
    )
    sec2 = DocumentSectionAggregate(
        id='sec-002', document_id='doc-001', title='S2',
        content_type='text', content='B', position=1,
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
        content_type='text', content='A', position=0,
    )
    sec2 = DocumentSectionAggregate(
        id='sec-002', document_id='doc-001', title='S2',
        content_type='text', content='B', position=1,
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
        content_type='text', content='A', position=0,
    )
    sec2 = DocumentSectionAggregate(
        id='sec-002', document_id='doc-001', title='S2',
        content_type='text', content='B', position=1,
    )
    doc_repo.save_section(sec1)
    doc_repo.save_section(sec2)
    doc_repo.embed_section('sec-001', [0.1, 0.2], 'test-model')
    doc_repo.embed_section('sec-002', [0.3, 0.4], 'test-model')

    doc_repo.delete('doc-001')
    assert doc_repo.get_embedding('sec-001') is None
    assert doc_repo.get_embedding('sec-002') is None
