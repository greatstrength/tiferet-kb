"""tiferet_kb Category Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..category import CategoryAggregate, CategoryNodeObject
from .settings import AggregateTestBase, NodeObjectTestBase

# *** constants

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = {
    'id': 'meeting-notes',
    'name': 'Meeting Notes',
    'description': 'Notes from meetings',
    'icon': '📝',
    'color': '#3B82F6',
}

# ** constant: equality_fields
EQUALITY_FIELDS = ['id', 'name', 'description', 'icon', 'color']


# *** classes

# ** class: TestCategoryAggregate
class TestCategoryAggregate(AggregateTestBase):
    '''Tests for CategoryAggregate.'''

    aggregate_cls = CategoryAggregate
    sample_data = AGGREGATE_SAMPLE_DATA
    equality_fields = EQUALITY_FIELDS

    set_attribute_params = [
        ('name',         'Updated Name',    None),
        ('description',  'New description', None),
        ('icon',         '📋',              None),
        ('color',        '#EF4444',         None),
        ('invalid_attr', 'value',           'INVALID_MODEL_ATTRIBUTE'),
    ]

    # *** domain-specific mutation tests

    # ** test: rename
    def test_rename(self, aggregate):
        '''Test the rename mutation method.'''

        aggregate.rename('Team Meeting Notes')
        assert aggregate.name == 'Team Meeting Notes'

    # ** test: set_description
    def test_set_description(self, aggregate):
        '''Test the set_description mutation method.'''

        aggregate.set_description('Updated description')
        assert aggregate.description == 'Updated description'

    # ** test: set_description_none
    def test_set_description_none(self, aggregate):
        '''Test clearing the description.'''

        aggregate.set_description(None)
        assert aggregate.description is None

    # ** test: set_icon
    def test_set_icon(self, aggregate):
        '''Test the set_icon mutation method.'''

        aggregate.set_icon('📋')
        assert aggregate.icon == '📋'

    # ** test: set_color
    def test_set_color(self, aggregate):
        '''Test the set_color mutation method.'''

        aggregate.set_color('#EF4444')
        assert aggregate.color == '#EF4444'


# ** class: TestCategoryNodeObject
class TestCategoryNodeObject(NodeObjectTestBase):
    '''Tests for CategoryNodeObject.'''

    node_cls = CategoryNodeObject
    aggregate_cls = CategoryAggregate
    sample_data = AGGREGATE_SAMPLE_DATA
    aggregate_sample_data = AGGREGATE_SAMPLE_DATA
    equality_fields = EQUALITY_FIELDS
    attrs_exclude_fields = ['id']
