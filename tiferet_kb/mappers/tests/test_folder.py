"""tiferet_kb Folder Mapper Tests"""

# *** imports

# ** app
from ..folder import FolderAggregate, FolderNodeObject
from .settings import AggregateTestBase, NodeObjectTestBase

# *** constants

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = {
    'id': 'f-001',
    'name': 'Projects',
    'parent_id': None,
    'path': '/Projects',
    'created_at': '2026-01-01T00:00:00+00:00',
}

# ** constant: equality_fields
EQUALITY_FIELDS = ['id', 'name', 'parent_id', 'path', 'created_at']


# *** classes

# ** class: TestFolderAggregate
class TestFolderAggregate(AggregateTestBase):
    '''Tests for FolderAggregate.'''

    aggregate_cls = FolderAggregate
    sample_data = AGGREGATE_SAMPLE_DATA
    equality_fields = EQUALITY_FIELDS

    set_attribute_params = [
        ('name',         'Updated Name', None),
        ('path',         '/updated',     None),
        ('invalid_attr', 'value',        'INVALID_MODEL_ATTRIBUTE'),
    ]

    # *** domain-specific mutation tests

    # ** test: rename
    def test_rename(self, aggregate):
        '''Test rename mutation.'''

        aggregate.rename('Engineering')
        assert aggregate.name == 'Engineering'

    # ** test: set_parent
    def test_set_parent(self, aggregate):
        '''Test set_parent mutation.'''

        aggregate.set_parent('f-002')
        assert aggregate.parent_id == 'f-002'

    # ** test: set_parent_none
    def test_set_parent_none(self, aggregate):
        '''Test setting parent to None (root).'''

        aggregate.set_parent(None)
        assert aggregate.parent_id is None

    # ** test: update_path
    def test_update_path(self, aggregate):
        '''Test update_path mutation.'''

        aggregate.update_path('/engineering/infra')
        assert aggregate.path == '/engineering/infra'


# ** class: TestFolderNodeObject
class TestFolderNodeObject(NodeObjectTestBase):
    '''Tests for FolderNodeObject.'''

    node_cls = FolderNodeObject
    aggregate_cls = FolderAggregate
    sample_data = AGGREGATE_SAMPLE_DATA
    aggregate_sample_data = AGGREGATE_SAMPLE_DATA
    equality_fields = EQUALITY_FIELDS
    attrs_exclude_fields = ['id']
