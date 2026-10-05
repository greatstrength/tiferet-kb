"""tiferet_kb Search Event Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.assets import TiferetError
from tiferet.assets.error import COMMAND_PARAMETER_REQUIRED_ID
from tiferet.events import DomainEvent

from ... import SearchComposedSections, SearchKeywordSections, SearchSimilarSections
from ...events import SearchComposedSections as EventsComposed
from ...events import SearchKeywordSections as EventsKeyword
from ...interfaces.document import DocumentService
from ..search import SearchComposedSections as ModuleComposed
from ..search import SearchKeywordSections as ModuleKeyword

# *** fixtures

# ** fixture: mock_document_service
@pytest.fixture
def mock_document_service():
    '''Mock DocumentService for testing.'''
    return mock.Mock(spec=DocumentService)

# *** tests

# ** test: search_keyword_sections_forwards_filters
def test_search_keyword_sections_forwards_filters(mock_document_service):
    '''SearchKeywordSections forwards limit and every filter, including None.'''

    mock_document_service.search_keyword.return_value = [
        {'section_id': 'sec-001', 'score': 0.5},
    ]

    results = DomainEvent.handle(
        SearchKeywordSections,
        dependencies={'document_service': mock_document_service},
        query='alpha',
        document_id=None,
    )

    assert results[0]['section_id'] == 'sec-001'
    mock_document_service.search_keyword.assert_called_once_with(
        query='alpha',
        limit=5,
        folder_id=None,
        category_id=None,
        document_id=None,
    )

# ** test: search_keyword_sections_requires_query
def test_search_keyword_sections_requires_query(mock_document_service):
    '''A missing query is the existing required-parameter error, not a new code.'''

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            SearchKeywordSections,
            dependencies={'document_service': mock_document_service},
        )
    assert exc_info.value.error_code == COMMAND_PARAMETER_REQUIRED_ID
    mock_document_service.search_keyword.assert_not_called()

# ** test: search_keyword_sections_forwards_blank_query
def test_search_keyword_sections_forwards_blank_query(mock_document_service):
    '''A blank query is forwarded and does not raise a new error.'''

    mock_document_service.search_keyword.return_value = []

    result = DomainEvent.handle(
        SearchKeywordSections,
        dependencies={'document_service': mock_document_service},
        query='',
    )

    assert result == []
    mock_document_service.search_keyword.assert_called_once_with(
        query='',
        limit=5,
        folder_id=None,
        category_id=None,
        document_id=None,
    )

    # Whitespace is a query too. It is not a missing parameter.
    mock_document_service.search_keyword.reset_mock()
    DomainEvent.handle(
        SearchKeywordSections,
        dependencies={'document_service': mock_document_service},
        query='   ',
    )
    mock_document_service.search_keyword.assert_called_once_with(
        query='   ',
        limit=5,
        folder_id=None,
        category_id=None,
        document_id=None,
    )

# ** test: search_composed_sections_forwards_vector_and_filters
def test_search_composed_sections_forwards_vector_and_filters(mock_document_service):
    '''SearchComposedSections forwards the vector and does not pass a model name.'''

    mock_document_service.search_composed.return_value = []

    DomainEvent.handle(
        SearchComposedSections,
        dependencies={'document_service': mock_document_service},
        query='alpha',
        query_embedding=[1.0, 0.0],
        folder_id='folder-1',
        category_id='cat-1',
        document_id='doc-1',
        limit=2,
    )

    mock_document_service.search_composed.assert_called_once_with(
        query='alpha',
        query_embedding=[1.0, 0.0],
        limit=2,
        folder_id='folder-1',
        category_id='cat-1',
        document_id='doc-1',
    )

# ** test: search_composed_sections_forwards_blank_query
def test_search_composed_sections_forwards_blank_query(mock_document_service):
    '''A blank query does not raise and does not drop the embedding side.'''

    embedding_hit = {'section_id': 'b-emb', 'score': 1 / 61}
    mock_document_service.search_composed.return_value = [embedding_hit]

    result = DomainEvent.handle(
        SearchComposedSections,
        dependencies={'document_service': mock_document_service},
        query='',
        query_embedding=[1.0, 0.0],
    )

    assert result == [embedding_hit]
    mock_document_service.search_composed.assert_called_once_with(
        query='',
        query_embedding=[1.0, 0.0],
        limit=5,
        folder_id=None,
        category_id=None,
        document_id=None,
    )

# ** test: search_events_are_exported_and_unregistered
def test_search_events_are_exported_and_unregistered():
    '''The search events are exported beside similar search and are not features.'''

    assert ModuleKeyword is SearchKeywordSections is EventsKeyword
    assert ModuleComposed is SearchComposedSections is EventsComposed
    assert SearchSimilarSections.__name__ == 'SearchSimilarSections'

    root = Path(__file__).resolve().parents[3]
    feature = (root / 'app' / 'configs' / 'feature.yml').read_text()
    container = (root / 'app' / 'configs' / 'container.yml').read_text()
    assert 'SearchKeywordSections' not in feature
    assert 'SearchComposedSections' not in feature
    assert 'SearchKeywordSections' not in container
    assert 'SearchComposedSections' not in container
