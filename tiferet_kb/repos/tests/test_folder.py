"""tiferet_kb Folder H5 Repository Integration Tests"""

# *** imports

# ** core
import os

# ** infra
import pytest
from tiferet.assets import TiferetError
from tiferet_h5.repos import NodeRepository, TableRepository
from tiferet_h5.utils import H5Client

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

# *** tests: RFP-001 storage alignment

# ** test_int: composes_node_repository_not_table_repository
def test_int_composes_node_repository_not_table_repository():
    '''The folder repository composes NodeRepository and not TableRepository.'''

    assert issubclass(FolderH5Repository, NodeRepository)
    assert not issubclass(FolderH5Repository, TableRepository)

# ** test_int: get_injects_group_name_as_id
def test_int_get_injects_group_name_as_id(folder_repo, h5_file, sample_folder):
    '''get returns the id that was the group name, and id is not stored as an attribute.'''

    folder_repo.save(sample_folder)

    assert folder_repo.get('f-001').id == 'f-001'
    with H5Client(path=h5_file, mode='r') as h5:
        assert 'id' not in h5.get_node_attrs('/kb/folders/f-001')

# ** test_int: list_none_and_root
def test_int_list_none_and_root(folder_repo):
    '''list(None) returns every folder and list('__root__') returns roots only.'''

    folder_repo.save(FolderAggregate(id='f-root', name='Root', path='/Root'))
    folder_repo.save(FolderAggregate(id='f-child', name='Child', path='/Root/Child', parent_id='f-root'))

    assert {f.id for f in folder_repo.list(None)} == {'f-root', 'f-child'}
    assert {f.id for f in folder_repo.list('__root__')} == {'f-root'}
    assert {f.id for f in folder_repo.list('f-root')} == {'f-child'}

# ** test_int: move_keeps_group
def test_int_move_keeps_group(folder_repo, sample_folder):
    '''move rewrites parent_id on the existing group and does not delete the node.'''

    folder_repo.save(sample_folder)
    folder_repo.move('f-001', 'f-002')

    assert folder_repo.exists('f-001') is True
    assert folder_repo.get('f-001').parent_id == 'f-002'

# ** test_int: missing_file_reads_are_empty_and_not_created
def test_int_missing_file_reads_are_empty_and_not_created(folder_repo, h5_file):
    '''Reads, delete, and move on a missing file do not create the file.'''

    assert folder_repo.get('nope') is None
    assert folder_repo.exists('nope') is False
    assert folder_repo.list() == []
    folder_repo.delete('nope')
    folder_repo.move('nope', 'x')

    assert not os.path.exists(h5_file)

# *** tests: RFP-008 visibility

# ** test_int: save_get_visibility_and_owner
def test_int_save_get_visibility_and_owner(folder_repo):
    '''A folder can store visibility and an optional owner, and get returns them.'''

    folder_repo.save(FolderAggregate(
        id='f-priv',
        name='Private',
        path='/Private',
        visibility='restricted',
        owner_id='owner-9',
    ))

    loaded = folder_repo.get('f-priv')
    assert loaded.visibility == 'restricted'
    assert loaded.owner_id == 'owner-9'
    assert loaded.visibility is not None

# ** test_int: list_visibility_conjoins_with_parent
def test_int_list_visibility_conjoins_with_parent(folder_repo):
    '''Visibility and owner filters conjoin with parent_id, and omission hides nothing.'''

    folder_repo.save(FolderAggregate(id='f-root', name='Root', path='/Root', visibility='public'))
    folder_repo.save(FolderAggregate(
        id='f-child', name='Child', path='/Root/Child', parent_id='f-root',
        visibility='private', owner_id='owner-1',
    ))
    folder_repo.save(FolderAggregate(
        id='f-other', name='Other', path='/Other', visibility='private', owner_id='owner-2',
    ))

    assert {f.id for f in folder_repo.list()} == {'f-root', 'f-child', 'f-other'}
    assert {f.id for f in folder_repo.list(parent_id='f-root', visibility='private')} == {'f-child'}
    assert {f.id for f in folder_repo.list('__root__', visibility='public')} == {'f-root'}
    assert folder_repo.list(owner_id='owner-1')[0].id == 'f-child'
    assert folder_repo.list(visibility='restricted') == []

# ** test_int: prechange_folder_reads_public_without_rewrite
def test_int_prechange_folder_reads_public_without_rewrite(folder_repo, h5_file):
    '''A folder written before these attributes exist reads as public with no owner.'''

    with H5Client(path=h5_file, mode='w') as h5:
        h5.create_group('/kb/folders/f-old')
        h5.set_node_attr('/kb/folders/f-old', 'name', 'Old')
        h5.set_node_attr('/kb/folders/f-old', 'path', '/Old')
        h5.set_node_attr('/kb/folders/f-old', 'created_at', '2026-01-01T00:00:00+00:00')

    loaded = folder_repo.get('f-old')
    assert loaded.visibility == 'public'
    assert loaded.owner_id is None
    assert loaded.name == 'Old'
    assert [f.id for f in folder_repo.list(visibility='public')] == ['f-old']
    assert folder_repo.list(visibility='private') == []
    assert folder_repo.list(owner_id='owner-1') == []

    with H5Client(path=h5_file, mode='r') as h5:
        attrs = h5.get_node_attrs('/kb/folders/f-old')
    assert 'visibility' not in attrs
    assert 'owner_id' not in attrs

# ** test_int: list_rejects_unknown_visibility
def test_int_list_rejects_unknown_visibility(folder_repo):
    '''An unrecognized visibility filter is KB_INVALID_VISIBILITY, not an empty list.'''

    with pytest.raises(TiferetError) as exc_info:
        folder_repo.list(visibility='published')
    assert exc_info.value.error_code == 'KB_INVALID_VISIBILITY'
