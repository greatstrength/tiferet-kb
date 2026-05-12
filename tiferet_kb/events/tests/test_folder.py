"""tiferet_kb Folder Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events import DomainEvent
from tiferet.assets import TiferetError

from ...interfaces.folder import FolderService
from ...interfaces.document import DocumentService
from ...mappers.folder import FolderAggregate
from ...mappers.document import DocumentAggregate
from ..folder import (
    AddFolder,
    GetFolder,
    ListFolderContents,
    MoveFolder,
    MoveDocument,
    RemoveFolder,
)

# *** fixtures

# ** fixture: mock_folder_service
@pytest.fixture
def mock_folder_service() -> FolderService:
    '''Mock FolderService for testing.'''
    return mock.Mock(spec=FolderService)


# ** fixture: mock_document_service
@pytest.fixture
def mock_document_service() -> DocumentService:
    '''Mock DocumentService for testing.'''
    return mock.Mock(spec=DocumentService)


# ** fixture: sample_folder
@pytest.fixture
def sample_folder() -> FolderAggregate:
    '''Sample FolderAggregate.'''
    return FolderAggregate(
        id='f-001', name='Projects', path='/Projects',
        created_at='2026-01-01T00:00:00+00:00',
    )


# ** fixture: sample_document
@pytest.fixture
def sample_document() -> DocumentAggregate:
    '''Sample DocumentAggregate.'''
    return DocumentAggregate(
        id='doc-001', title='Test Doc', folder_id='f-001',
    )

# *** tests

# ** test: add_folder_success
def test_add_folder_success(mock_folder_service):
    '''Test successful creation of a folder.'''

    mock_folder_service.exists.return_value = False
    mock_folder_service.get.return_value = None

    result = DomainEvent.handle(
        AddFolder,
        dependencies={'folder_service': mock_folder_service},
        name='Projects',
    )

    assert result.name == 'Projects'
    assert result.path == '/Projects'
    mock_folder_service.save.assert_called_once()


# ** test: add_folder_with_parent
def test_add_folder_with_parent(mock_folder_service, sample_folder):
    '''Test creating a nested folder.'''

    mock_folder_service.exists.return_value = False
    mock_folder_service.get.return_value = sample_folder

    result = DomainEvent.handle(
        AddFolder,
        dependencies={'folder_service': mock_folder_service},
        name='Design',
        parent_id='f-001',
    )

    assert result.name == 'Design'
    assert result.path == '/Projects/Design'
    assert result.parent_id == 'f-001'


# ** test: add_folder_duplicate
def test_add_folder_duplicate(mock_folder_service):
    '''Test that adding a duplicate folder raises.'''

    mock_folder_service.exists.return_value = True

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddFolder,
            dependencies={'folder_service': mock_folder_service},
            name='Dup',
            id='existing',
        )


# ** test: get_folder_success
def test_get_folder_success(mock_folder_service, sample_folder):
    '''Test successful folder retrieval.'''

    mock_folder_service.get.return_value = sample_folder

    result = DomainEvent.handle(
        GetFolder,
        dependencies={'folder_service': mock_folder_service},
        id='f-001',
    )

    assert result is sample_folder


# ** test: get_folder_not_found
def test_get_folder_not_found(mock_folder_service):
    '''Test not-found raises.'''

    mock_folder_service.get.return_value = None

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            GetFolder,
            dependencies={'folder_service': mock_folder_service},
            id='nonexistent',
        )


# ** test: list_folder_contents_success
def test_list_folder_contents_success(mock_folder_service, mock_document_service, sample_folder, sample_document):
    '''Test listing folder contents.'''

    mock_folder_service.exists.return_value = True
    mock_folder_service.list.return_value = []
    mock_document_service.list.return_value = [sample_document]

    result = DomainEvent.handle(
        ListFolderContents,
        dependencies={
            'folder_service': mock_folder_service,
            'document_service': mock_document_service,
        },
        folder_id='f-001',
    )

    assert 'folders' in result
    assert 'documents' in result
    assert len(result['documents']) == 1


# ** test: list_folder_contents_not_found
def test_list_folder_contents_not_found(mock_folder_service, mock_document_service):
    '''Test that listing contents of a non-existent folder raises.'''

    mock_folder_service.exists.return_value = False

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            ListFolderContents,
            dependencies={
                'folder_service': mock_folder_service,
                'document_service': mock_document_service,
            },
            folder_id='nonexistent',
        )


# ** test: move_folder_success
def test_move_folder_success(mock_folder_service, sample_folder):
    '''Test moving a folder to a new parent.'''

    parent = FolderAggregate(id='f-002', name='Engineering', path='/Engineering')
    mock_folder_service.get.side_effect = lambda id: sample_folder if id == 'f-001' else parent

    result = DomainEvent.handle(
        MoveFolder,
        dependencies={'folder_service': mock_folder_service},
        id='f-001',
        new_parent_id='f-002',
    )

    assert result.parent_id == 'f-002'
    assert result.path == '/Engineering/Projects'


# ** test: move_folder_circular_reference
def test_move_folder_circular_reference(mock_folder_service, sample_folder):
    '''Test that moving a folder to itself raises.'''

    mock_folder_service.get.return_value = sample_folder

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            MoveFolder,
            dependencies={'folder_service': mock_folder_service},
            id='f-001',
            new_parent_id='f-001',
        )


# ** test: move_document_success
def test_move_document_success(mock_document_service, sample_document):
    '''Test moving a document to a different folder.'''

    mock_document_service.get.return_value = sample_document

    result = DomainEvent.handle(
        MoveDocument,
        dependencies={'document_service': mock_document_service},
        document_id='doc-001',
        folder_id='f-002',
    )

    assert result == 'doc-001'
    mock_document_service.save.assert_called_once()


# ** test: move_document_not_found
def test_move_document_not_found(mock_document_service):
    '''Test that moving a non-existent document raises.'''

    mock_document_service.get.return_value = None

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            MoveDocument,
            dependencies={'document_service': mock_document_service},
            document_id='nonexistent',
        )


# ** test: remove_folder_success
def test_remove_folder_success(mock_folder_service, mock_document_service, sample_document):
    '''Test removing a folder unfiles its documents.'''

    mock_document_service.list.return_value = [sample_document]

    result = DomainEvent.handle(
        RemoveFolder,
        dependencies={
            'folder_service': mock_folder_service,
            'document_service': mock_document_service,
        },
        id='f-001',
    )

    assert result == 'f-001'
    mock_folder_service.delete.assert_called_once_with('f-001')
    mock_document_service.save.assert_called_once()
