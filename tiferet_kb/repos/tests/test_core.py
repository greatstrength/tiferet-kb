"""tiferet_kb Core H5 Repository Tests"""

# *** imports

# ** infra
import numpy as np
import pytest
from tiferet_h5.repos import H5Repository, NodeRepository, TableRepository

# ** app
from ...mappers.template import TemplateTableObject
from ..category import CategoryH5Repository
from ..core import SCHEMA_VERSION_ATTR, KBNodeRepository, KBTableRepository
from ..document import DocumentH5Repository
from ..folder import FolderH5Repository
from ..template import (
    TemplateH5Repository,
    TemplateSectionTableRepository,
    TemplateTableRepository,
)

# *** fixtures

# ** fixture: node_repo
@pytest.fixture
def node_repo(tmp_path) -> KBNodeRepository:
    '''Provide a KBNodeRepository backed by a temporary HDF5 file.'''
    return KBNodeRepository(h5_file=str(tmp_path / 'test_core.h5'))

# ** fixture: table_repo
@pytest.fixture
def table_repo(tmp_path) -> KBTableRepository:
    '''Provide a KBTableRepository backed by a temporary HDF5 file.'''
    return KBTableRepository(h5_file=str(tmp_path / 'test_core.h5'))

# *** tests

# ** test: core_repos_extend_the_h5_mixins
def test_core_repos_extend_the_h5_mixins():
    '''Each core repo extends exactly one tiferet-h5 mixin beside H5Repository.'''

    assert issubclass(KBNodeRepository, NodeRepository)
    assert issubclass(KBNodeRepository, H5Repository)
    assert not issubclass(KBNodeRepository, TableRepository)
    assert issubclass(KBTableRepository, TableRepository)
    assert issubclass(KBTableRepository, H5Repository)
    assert not issubclass(KBTableRepository, NodeRepository)

# ** test: repos_extend_the_matching_core_repo
def test_repos_extend_the_matching_core_repo():
    '''Node repos extend KBNodeRepository, table collaborators extend KBTableRepository, and the service repos extend neither.'''

    assert issubclass(CategoryH5Repository, KBNodeRepository)
    assert issubclass(FolderH5Repository, KBNodeRepository)
    assert issubclass(TemplateTableRepository, KBTableRepository)
    assert issubclass(TemplateSectionTableRepository, KBTableRepository)

    for repo_cls in (DocumentH5Repository, TemplateH5Repository):
        assert issubclass(repo_cls, H5Repository)
        assert not issubclass(repo_cls, NodeRepository)
        assert not issubclass(repo_cls, TableRepository)

# ** test: document_repo_holds_both_collaborators
def test_document_repo_holds_both_collaborators(tmp_path):
    '''The document repository composes one node and one table collaborator.'''

    repo = DocumentH5Repository(h5_file=str(tmp_path / 'test_core.h5'))

    assert isinstance(repo.node_repo, KBNodeRepository)
    assert isinstance(repo.table_repo, KBTableRepository)

# ** test: remove_node_group_recursive
def test_remove_node_group_recursive(node_repo):
    '''A group and its children are removed with recursive=True.'''

    with node_repo.client() as h5:
        h5.create_group('/kb/a/child')
        node_repo.remove_node(h5, '/kb/a', recursive=True)
        assert not h5.node_exists('/kb/a')
        assert h5.node_exists('/kb')

# ** test: remove_node_array
def test_remove_node_array(node_repo):
    '''An array is removed with the default recursive=False.'''

    with node_repo.client() as h5:
        h5.create_array('/kb/arr', np.zeros((2, 2), dtype=np.float32))
        node_repo.remove_node(h5, '/kb/arr')
        assert not h5.node_exists('/kb/arr')

# ** test: remove_node_missing
def test_remove_node_missing(node_repo):
    '''A missing node is not an error.'''

    with node_repo.client() as h5:
        node_repo.remove_node(h5, '/kb/nothing', recursive=True)
        node_repo.remove_node(h5, '/kb/nothing')

# ** test: ensure_table_stamps_on_create_only
def test_ensure_table_stamps_on_create_only(table_repo):
    '''The fingerprint is stamped on create and never rewritten afterwards.'''

    path = '/kb/templates/templates'

    with table_repo.client() as h5:
        table_repo.ensure_table(h5, path, TemplateTableObject, title='Templates')
        stamp = h5.get_node_attr(path, SCHEMA_VERSION_ATTR)
        assert stamp == TemplateTableObject.schema_fingerprint()

        # A later call returns the table without rewriting the stamp.
        h5.set_node_attr(path, SCHEMA_VERSION_ATTR, 'custom')
        table_repo.ensure_table(h5, path, TemplateTableObject)
        assert h5.get_node_attr(path, SCHEMA_VERSION_ATTR) == 'custom'
