"""tiferet_kb Document Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events import DomainEvent
from tiferet.assets import TiferetError

from ...interfaces.document import DocumentService
from ...mappers.document import DocumentAggregate
from ..document import (
    AddDocument,
    GetDocument,
    ListDocuments,
    UpdateDocument,
    RemoveDocument,
)

# *** fixtures

# ** fixture: mock_document_service
@pytest.fixture
def mock_document_service() -> DocumentService:
    '''Mock DocumentService for testing.'''
    return mock.Mock(spec=DocumentService)


# ** fixture: sample_document
@pytest.fixture
def sample_document() -> DocumentAggregate:
    '''Sample DocumentAggregate instance for testing.'''
    return DocumentAggregate(
        id='doc-001',
        title='Test Document',
        status='draft',
        created_at='2026-01-01T00:00:00+00:00',
        updated_at='2026-01-01T00:00:00+00:00',
    )

# *** tests

# ** test: add_document_success
def test_add_document_success(mock_document_service):
    '''Test successful creation of a new document.'''

    mock_document_service.exists.return_value = False

    result = DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': mock_document_service},
        title='My New Document',
    )

    assert result.title == 'My New Document'
    assert result.status == 'draft'
    assert result.id is not None
    mock_document_service.save.assert_called_once()


# ** test: add_document_with_explicit_id
def test_add_document_with_explicit_id(mock_document_service):
    '''Test creation with an explicit ID.'''

    mock_document_service.exists.return_value = False

    result = DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': mock_document_service},
        title='Test',
        id='custom-id',
    )

    assert result.id == 'custom-id'


# ** test: add_document_duplicate
def test_add_document_duplicate(mock_document_service):
    '''Test that adding a duplicate document raises an error.'''

    mock_document_service.exists.return_value = True

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddDocument,
            dependencies={'document_service': mock_document_service},
            title='Test',
            id='existing-id',
        )


# ** test: add_document_missing_title
def test_add_document_missing_title(mock_document_service):
    '''Test that AddDocument raises when title is missing.'''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddDocument,
            dependencies={'document_service': mock_document_service},
        )


# ** test: get_document_success
def test_get_document_success(mock_document_service, sample_document):
    '''Test successful retrieval of a document.'''

    mock_document_service.get.return_value = sample_document

    result = DomainEvent.handle(
        GetDocument,
        dependencies={'document_service': mock_document_service},
        id='doc-001',
    )

    assert result is sample_document


# ** test: get_document_not_found
def test_get_document_not_found(mock_document_service):
    '''Test that getting a non-existent document raises.'''

    mock_document_service.get.return_value = None

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            GetDocument,
            dependencies={'document_service': mock_document_service},
            id='nonexistent',
        )


# ** test: list_documents_success
def test_list_documents_success(mock_document_service, sample_document):
    '''Test listing documents.'''

    mock_document_service.list.return_value = [sample_document]

    result = DomainEvent.handle(
        ListDocuments,
        dependencies={'document_service': mock_document_service},
    )

    assert len(result) == 1


# ** test: list_documents_with_filters
def test_list_documents_with_filters(mock_document_service):
    '''Test listing documents with filters.'''

    mock_document_service.list.return_value = []

    DomainEvent.handle(
        ListDocuments,
        dependencies={'document_service': mock_document_service},
        folder_id='folder-1',
        status='draft',
    )

    mock_document_service.list.assert_called_once_with(
        folder_id='folder-1',
        category_id=None,
        status='draft',
    )


# ** test: update_document_success
def test_update_document_success(mock_document_service, sample_document):
    '''Test successful update of a document attribute.'''

    mock_document_service.get.return_value = sample_document

    result = DomainEvent.handle(
        UpdateDocument,
        dependencies={'document_service': mock_document_service},
        id='doc-001',
        attribute='title',
        value='Updated Title',
    )

    assert result.title == 'Updated Title'
    mock_document_service.save.assert_called_once()


# ** test: update_document_invalid_attribute
def test_update_document_invalid_attribute(mock_document_service):
    '''Test that updating an invalid attribute raises.'''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            UpdateDocument,
            dependencies={'document_service': mock_document_service},
            id='doc-001',
            attribute='nonexistent',
            value='bad',
        )


# ** test: update_document_invalid_status
def test_update_document_invalid_status(mock_document_service):
    '''Test that an invalid status value raises.'''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            UpdateDocument,
            dependencies={'document_service': mock_document_service},
            id='doc-001',
            attribute='status',
            value='invalid_status',
        )


# ** test: remove_document_success
def test_remove_document_success(mock_document_service):
    '''Test successful removal of a document.'''

    result = DomainEvent.handle(
        RemoveDocument,
        dependencies={'document_service': mock_document_service},
        id='doc-001',
    )

    assert result == 'doc-001'
    mock_document_service.delete.assert_called_once_with('doc-001')
