"""tiferet_kb Tag Mapper Tests"""

# *** imports

# ** app
from ..tag import TagAggregate, TagNodeObject
from .core import AggregateTestBase, NodeObjectTestBase

# *** constants

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = {
    'id': 'release',
    'name': 'Release',
    'color': '#3B82F6',
}

# ** constant: equality_fields
EQUALITY_FIELDS = ['id', 'name', 'color']

# *** classes

# ** class: TestTagAggregate
class TestTagAggregate(AggregateTestBase):
    '''Tests for TagAggregate.'''

    aggregate_cls = TagAggregate
    sample_data = AGGREGATE_SAMPLE_DATA
    equality_fields = EQUALITY_FIELDS

    set_attribute_params = [
        ('name', 'Updated Name', None),
        ('color', '#EF4444', None),
        ('invalid_attr', 'value', 'INVALID_MODEL_ATTRIBUTE'),
    ]

    # ** test: rename
    def test_rename(self, aggregate):
        '''Test the rename mutation method.'''

        aggregate.rename('Ship')
        assert aggregate.name == 'Ship'

    # ** test: set_color
    def test_set_color(self, aggregate):
        '''Test the set_color mutation method.'''

        aggregate.set_color('#EF4444')
        assert aggregate.color == '#EF4444'

    # ** test: set_color_none
    def test_set_color_none(self, aggregate):
        '''Test clearing the color.'''

        aggregate.set_color(None)
        assert aggregate.color is None

    # ** test: update
    def test_update(self, aggregate):
        '''The generic update mutator renames, recolors, and clears color.'''

        aggregate.update('name', 'Ship')
        aggregate.update('color', None)
        assert aggregate.name == 'Ship'
        assert aggregate.color is None

# ** class: TestTagNodeObject
class TestTagNodeObject(NodeObjectTestBase):
    '''Tests for TagNodeObject.'''

    node_cls = TagNodeObject
    aggregate_cls = TagAggregate
    sample_data = AGGREGATE_SAMPLE_DATA
    aggregate_sample_data = AGGREGATE_SAMPLE_DATA
    equality_fields = EQUALITY_FIELDS
    attrs_exclude_fields = ['id']
