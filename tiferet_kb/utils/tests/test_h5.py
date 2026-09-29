"""tiferet_kb H5 Utility Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import numpy as np
import pytest

# ** app
from tiferet_h5.utils import H5Client

from ...mappers.template import TemplateTableObject
from ..h5 import SCHEMA_VERSION_ATTR, ensure_table, remove_node

# *** fixtures

# ** fixture: h5_path
@pytest.fixture
def h5_path(tmp_path) -> Path:
    '''Provide a temporary HDF5 file path.'''
    return tmp_path / 'test_h5_util.h5'

# *** tests

# ** test: remove_node_group_recursive
def test_remove_node_group_recursive(h5_path):
    '''A group and its children are removed with recursive=True.'''

    with H5Client(path=h5_path, mode='a') as h5:
        h5.create_group('/kb/a/child')
        remove_node(h5, '/kb/a', recursive=True)
        assert not h5.node_exists('/kb/a')
        assert h5.node_exists('/kb')


# ** test: remove_node_array
def test_remove_node_array(h5_path):
    '''An array is removed with the default recursive=False.'''

    with H5Client(path=h5_path, mode='a') as h5:
        h5.create_array('/kb/arr', np.zeros((2, 2), dtype=np.float32))
        remove_node(h5, '/kb/arr')
        assert not h5.node_exists('/kb/arr')


# ** test: remove_node_missing
def test_remove_node_missing(h5_path):
    '''A missing node is not an error.'''

    with H5Client(path=h5_path, mode='a') as h5:
        remove_node(h5, '/kb/nothing', recursive=True)
        remove_node(h5, '/kb/nothing')


# ** test: ensure_table_stamps_on_create_only
def test_ensure_table_stamps_on_create_only(h5_path):
    '''The fingerprint is stamped on create and never rewritten afterwards.'''

    path = '/kb/templates/templates'

    with H5Client(path=h5_path, mode='a') as h5:
        ensure_table(h5, path, TemplateTableObject, title='Templates')
        stamp = h5.get_node_attr(path, SCHEMA_VERSION_ATTR)
        assert stamp == TemplateTableObject.schema_fingerprint()

        # A later call returns the table without rewriting the stamp.
        h5.set_node_attr(path, SCHEMA_VERSION_ATTR, 'custom')
        ensure_table(h5, path, TemplateTableObject)
        assert h5.get_node_attr(path, SCHEMA_VERSION_ATTR) == 'custom'
