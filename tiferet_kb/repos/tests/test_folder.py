"""tiferet_kb Folder H5 Repository Integration Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...mappers.folder import FolderAggregate
from ..folder import FolderH5Repository

# *** fixtures

# ** fixture: h5_file
@pytest.fixture
def h5_file(tmp_path) -> str:
    '''Provide a temporary HDF5 file path.'''
    return str(tmp_path / 'test_kb.h5')


# ** fixture: folder_repo
@pytest.fixture
def folder_repo(h5_file: str) -> FolderH5Repository:
    '''Provide a FolderH5Repository backed by a temporary HDF5 file.'''
    return FolderH5Repository(h5_file=h5_file)


# ** fixture: sample_folder
@pytest.fixture
def sample_folder() -> FolderAggregate:
    '''Provide a sample FolderAggregate.'''
    return FolderAggregate(
        id='f-001',
        name='Projects',
        path='/Projects',
        created_at='2026-01-01T00:00:00+00:00',
    )

# *** tests

# ** test_int: save_and_exists
def test_int_save_and_exists(folder_repo, sample_folder):
    '''Test that saving a folder makes it exist.'''

    folder_repo.save(sample_folder)
    assert folder_repo.exists('f-001') is True


# ** test_int: exists_negative
def test_int_exists_negative(folder_repo, sample_folder):
    '''Test that exists returns False for non-existent.'''

    folder_repo.save(sample_folder)
    assert folder_repo.exists('nonexistent') is False


# ** test_int: get_success
def test_int_get_success(folder_repo, sample_folder):
    '''Test successful retrieval.'''

    folder_repo.save(sample_folder)
    result = folder_repo.get('f-001')

    assert result is not None
    assert result.id == 'f-001'
    assert result.name == 'Projects'
    assert result.path == '/Projects'


# ** test_int: get_not_found
def test_int_get_not_found(folder_repo, sample_folder):
    '''Test get returns None for non-existent.'''

    folder_repo.save(sample_folder)
    assert folder_repo.get('nonexistent') is None


# ** test_int: list_all
def test_int_list_all(folder_repo):
    '''Test listing all folders.'''

    folder_repo.save(FolderAggregate(id='f-001', name='Projects', path='/Projects'))
    folder_repo.save(FolderAggregate(id='f-002', name='Archive', path='/Archive'))

    result = folder_repo.list()
    assert len(result) == 2


# ** test_int: list_by_parent
def test_int_list_by_parent(folder_repo):
    '''Test listing folders filtered by parent_id.'''

    folder_repo.save(FolderAggregate(id='f-001', name='Projects', path='/Projects'))
    folder_repo.save(FolderAggregate(id='f-002', name='Design', path='/Projects/Design', parent_id='f-001'))
    folder_repo.save(FolderAggregate(id='f-003', name='Archive', path='/Archive'))

    result = folder_repo.list(parent_id='f-001')
    assert len(result) == 1
    assert result[0].id == 'f-002'


# ** test_int: list_empty
def test_int_list_empty(folder_repo):
    '''Test listing when no folders exist.'''

    assert folder_repo.list() == []


# ** test_int: save_update
def test_int_save_update(folder_repo, sample_folder):
    '''Test that saving an existing folder updates it.'''

    folder_repo.save(sample_folder)
    sample_folder.rename('Engineering')
    folder_repo.save(sample_folder)

    result = folder_repo.get('f-001')
    assert result.name == 'Engineering'


# ** test_int: delete_success
def test_int_delete_success(folder_repo, sample_folder):
    '''Test deleting a folder.'''

    folder_repo.save(sample_folder)
    folder_repo.delete('f-001')

    assert folder_repo.exists('f-001') is False


# ** test_int: delete_idempotent
def test_int_delete_idempotent(folder_repo, sample_folder):
    '''Test that deleting a non-existent folder is idempotent.'''

    folder_repo.save(sample_folder)
    folder_repo.delete('nonexistent')  # Should not raise


# ** test_int: move
def test_int_move(folder_repo, sample_folder):
    '''Test moving a folder updates its parent_id attribute.'''

    folder_repo.save(sample_folder)
    folder_repo.move('f-001', 'f-002')

    result = folder_repo.get('f-001')
    assert result.parent_id == 'f-002'


# ** test_int: move_to_root
def test_int_move_to_root(folder_repo):
    '''Test moving a folder to root (None parent).'''

    folder = FolderAggregate(id='f-002', name='Design', path='/Projects/Design', parent_id='f-001')
    folder_repo.save(folder)

    folder_repo.move('f-002', None)

    result = folder_repo.get('f-002')
    # parent_id should be empty string (stored as '') which maps back via attrs.
    assert result.parent_id in (None, '')
