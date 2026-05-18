"""tiferet_kb Embedding Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events import DomainEvent
from tiferet.assets import TiferetError

from ...assets import constants as const
from ...interfaces.document import DocumentService
from ...mappers.document import DocumentSectionAggregate
from ..embedding import EmbedDocumentSections, SearchSimilarSections, RemoveEmbedding

# *** fixtures

# ** fixture: mock_document_service
@pytest.fixture
def mock_document_service():
    '''Mock DocumentService for testing.'''
    return mock.Mock(spec=DocumentService)


# ** fixture: sample_sections
@pytest.fixture
def sample_sections():
    '''Sample document section aggregates.'''
    return [
        DocumentSectionAggregate(
            id='sec-001',
            document_id='doc-001',
            title='Introduction',
            content_type='markdown',
            position=0,
        ),
        DocumentSectionAggregate(
            id='sec-002',
            document_id='doc-001',
            title='Conclusion',
            content_type='markdown',
            position=1,
        ),
    ]


# *** tests

# ** test: embed_document_sections_success
def test_embed_document_sections_success(mock_document_service, sample_sections):
    '''
    Test successful batch embedding of document sections.
    '''

    # Arrange.
    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = sample_sections

    embeddings = {
        'sec-001': [0.1, 0.2, 0.3],
        'sec-002': [0.4, 0.5, 0.6],
    }

    # Execute.
    result = DomainEvent.handle(
        EmbedDocumentSections,
        dependencies={'document_service': mock_document_service},
        document_id='doc-001',
        embeddings=embeddings,
        model_name='test-model',
    )

    # Assert.
    assert result == 2
    assert mock_document_service.embed_section.call_count == 2


# ** test: embed_document_sections_document_not_found
def test_embed_document_sections_document_not_found(mock_document_service):
    '''
    Test that embedding fails when the document does not exist.
    '''

    # Arrange.
    mock_document_service.exists.return_value = False

    # Execute and assert.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            EmbedDocumentSections,
            dependencies={'document_service': mock_document_service},
            document_id='missing-doc',
            embeddings={'sec-001': [0.1]},
            model_name='test-model',
        )
    assert exc_info.value.error_code == const.KB_DOCUMENT_NOT_FOUND_ID


# ** test: embed_document_sections_section_not_found
def test_embed_document_sections_section_not_found(mock_document_service, sample_sections):
    '''
    Test that embedding fails when a section ID does not belong to the document.
    '''

    # Arrange.
    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = sample_sections

    # Execute with a nonexistent section ID.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            EmbedDocumentSections,
            dependencies={'document_service': mock_document_service},
            document_id='doc-001',
            embeddings={'nonexistent': [0.1]},
            model_name='test-model',
        )
    assert exc_info.value.error_code == const.KB_DOCUMENT_SECTION_NOT_FOUND_ID


# ** test: search_similar_sections_success
def test_search_similar_sections_success(mock_document_service):
    '''
    Test successful semantic search.
    '''

    # Arrange.
    mock_document_service.search_similar.return_value = [
        {'section_id': 'sec-001', 'score': 0.95},
        {'section_id': 'sec-002', 'score': 0.80},
    ]

    # Execute.
    results = DomainEvent.handle(
        SearchSimilarSections,
        dependencies={'document_service': mock_document_service},
        query_embedding=[0.1, 0.2, 0.3],
        limit=5,
    )

    # Assert.
    assert len(results) == 2
    assert results[0]['section_id'] == 'sec-001'
    assert results[0]['score'] == 0.95
    mock_document_service.search_similar.assert_called_once_with(
        query_embedding=[0.1, 0.2, 0.3],
        limit=5,
        folder_id=None,
        category_id=None,
    )


# ** test: search_similar_sections_with_filters
def test_search_similar_sections_with_filters(mock_document_service):
    '''
    Test semantic search with folder and category filters.
    '''

    # Arrange.
    mock_document_service.search_similar.return_value = []

    # Execute.
    results = DomainEvent.handle(
        SearchSimilarSections,
        dependencies={'document_service': mock_document_service},
        query_embedding=[0.1, 0.2, 0.3],
        folder_id='folder-001',
        category_id='cat-001',
    )

    # Assert.
    assert results == []
    mock_document_service.search_similar.assert_called_once_with(
        query_embedding=[0.1, 0.2, 0.3],
        limit=5,
        folder_id='folder-001',
        category_id='cat-001',
    )


# ** test: remove_embedding_success
def test_remove_embedding_success(mock_document_service):
    '''
    Test successful embedding removal.
    '''

    # Arrange.
    mock_document_service.get_embedding.return_value = [0.1, 0.2, 0.3]

    # Execute.
    result = DomainEvent.handle(
        RemoveEmbedding,
        dependencies={'document_service': mock_document_service},
        section_id='sec-001',
    )

    # Assert.
    assert result == 'sec-001'
    mock_document_service.remove_embedding.assert_called_once_with('sec-001')


# ** test: remove_embedding_not_embedded
def test_remove_embedding_not_embedded(mock_document_service):
    '''
    Test that removing a non-existent embedding raises an error.
    '''

    # Arrange.
    mock_document_service.get_embedding.return_value = None

    # Execute and assert.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            RemoveEmbedding,
            dependencies={'document_service': mock_document_service},
            section_id='sec-999',
        )
    assert exc_info.value.error_code == const.KB_SECTION_NOT_EMBEDDED_ID
