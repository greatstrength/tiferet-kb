"""tiferet_kb Folder Domain Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..folder import Folder

# *** tests

# ** test: folder_auto_generates_defaults
def test_folder_auto_generates_defaults():
    '''Test that Folder auto-generates id, path, and created_at.'''

    folder = Folder(name='Projects')
    assert folder.id is not None and len(folder.id) == 36
    assert folder.path == '/Projects'
    assert folder.created_at is not None
    assert folder.parent_id is None


# ** test: folder_preserves_explicit_values
def test_folder_preserves_explicit_values():
    '''Test that explicit id and path are preserved.'''

    folder = Folder(id='f-001', name='Design', path='/projects/design')
    assert folder.id == 'f-001'
    assert folder.path == '/projects/design'


# ** test: folder_with_parent
def test_folder_with_parent():
    '''Test folder with parent_id.'''

    folder = Folder(name='Design', parent_id='f-001', path='/projects/design')
    assert folder.parent_id == 'f-001'


# ** test: folder_rejects_extra_fields
def test_folder_rejects_extra_fields():
    '''Test that extra fields are rejected.'''

    with pytest.raises(Exception):
        Folder(name='Test', unknown_field='bad')
