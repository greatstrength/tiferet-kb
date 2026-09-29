"""tiferet_kb Core H5 Repository Tests"""

# *** imports

# ** infra
import numpy as np
import pytest
from tiferet_h5.repos import H5Repository

# ** app
from ...mappers.template import TemplateTableObject
from ..category import CategoryH5Repository
from ..core import SCHEMA_VERSION_ATTR, KBH5Repository
from ..document import DocumentH5Repository
from ..folder import FolderH5Repository
from ..template import (
    TemplateH5Repository,
    TemplateSectionTableRepository,
    TemplateTableRepository,
)

# *** fixtures

# ** fixture: core_repo
@pytest.fixture
def core_repo(tmp_path) -> KBH5Repository:
    '''Provide a KBH5Repository backed by a temporary HDF5 file.'''
    return KBH5Repository(h5_file=str(tmp_path / 'test_core.h5'))

# *** tests

# ** test: every_repo_extends_core
def test_every_repo_extends_core():
    '''Every kb repository extends KBH5Repository, which is an H5Repository.'''

    assert issubclass(KBH5Repository, H5Repository)
    for repo_cls in (
        CategoryH5Repository,
        FolderH5Repository,
        DocumentH5Repository,
        TemplateH5Repository,
        TemplateTableRepository,
        TemplateSectionTableRepository,
    ):
        assert issubclass(repo_cls, KBH5Repository)

# ** test: remove_node_group_recursive
def test_remove_node_group_recursive(core_repo):
    '''A group and its children are removed with recursive=True.'''

    with core_repo.client() as h5:
        h5.create_group('/kb/a/child')
        core_repo.remove_node(h5, '/kb/a', recursive=True)
        assert not h5.node_exists('/kb/a')
        assert h5.node_exists('/kb')

# ** test: remove_node_array
def test_remove_node_array(core_repo):
    '''An array is removed with the default recursive=False.'''

    with core_repo.client() as h5:
        h5.create_array('/kb/arr', np.zeros((2, 2), dtype=np.float32))
        core_repo.remove_node(h5, '/kb/arr')
        assert not h5.node_exists('/kb/arr')

# ** test: remove_node_missing
def test_remove_node_missing(core_repo):
    '''A missing node is not an error.'''

    with core_repo.client() as h5:
        core_repo.remove_node(h5, '/kb/nothing', recursive=True)
        core_repo.remove_node(h5, '/kb/nothing')

# ** test: ensure_table_stamps_on_create_only
def test_ensure_table_stamps_on_create_only(core_repo):
    '''The fingerprint is stamped on create and never rewritten afterwards.'''

    path = '/kb/templates/templates'

    with core_repo.client() as h5:
        core_repo.ensure_table(h5, path, TemplateTableObject, title='Templates')
        stamp = h5.get_node_attr(path, SCHEMA_VERSION_ATTR)
        assert stamp == TemplateTableObject.schema_fingerprint()

        # A later call returns the table without rewriting the stamp.
        h5.set_node_attr(path, SCHEMA_VERSION_ATTR, 'custom')
        core_repo.ensure_table(h5, path, TemplateTableObject)
        assert h5.get_node_attr(path, SCHEMA_VERSION_ATTR) == 'custom'
