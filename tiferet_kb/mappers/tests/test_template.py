"""tiferet_kb Template Mapper Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
import tables

# ** app
from ..template import (
    TemplateAggregate,
    TemplateSectionAggregate,
    TemplateTableObject,
    TemplateSectionTableObject,
)
from .settings import AggregateTestBase

# *** constants

# ** constant: tmpl_sample_data
TMPL_SAMPLE_DATA = {
    'id': 'tmpl-001',
    'name': 'Meeting Notes',
    'description': 'Template for meeting notes',
    'category_id': 'meetings',
    'created_at': '2026-01-01T00:00:00+00:00',
    'updated_at': '2026-01-01T00:00:00+00:00',
}

# ** constant: tmpl_equality_fields
TMPL_EQUALITY_FIELDS = ['id', 'name', 'description', 'created_at']

# ** constant: sec_sample_data
SEC_SAMPLE_DATA = {
    'id': 'tsec-001',
    'template_id': 'tmpl-001',
    'title': 'Agenda',
    'content_type': 'markdown',
    'default_content': '## Agenda\n- Item 1',
    'position': 0,
}

# ** constant: sec_equality_fields
SEC_EQUALITY_FIELDS = ['id', 'template_id', 'title', 'content_type', 'default_content', 'position']


# *** classes

# ** class: TestTemplateAggregate
class TestTemplateAggregate(AggregateTestBase):
    '''Tests for TemplateAggregate.'''

    aggregate_cls = TemplateAggregate
    sample_data = TMPL_SAMPLE_DATA
    equality_fields = TMPL_EQUALITY_FIELDS

    set_attribute_params = [
        ('name',         'Updated Name',    None),
        ('description',  'New description', None),
        ('invalid_attr', 'value',           'INVALID_MODEL_ATTRIBUTE'),
    ]

    # *** domain-specific mutation tests

    # ** test: rename
    def test_rename(self, aggregate):
        '''Test rename updates name and timestamp.'''

        old_updated = aggregate.updated_at
        aggregate.rename('Sprint Retro Template')
        assert aggregate.name == 'Sprint Retro Template'
        assert aggregate.updated_at != old_updated

    # ** test: set_description
    def test_set_description(self, aggregate):
        '''Test set_description mutation.'''

        aggregate.set_description('Updated desc')
        assert aggregate.description == 'Updated desc'

    # ** test: set_category
    def test_set_category(self, aggregate):
        '''Test set_category mutation.'''

        aggregate.set_category('design-docs')
        assert aggregate.category_id == 'design-docs'


# ** class: TestTemplateSectionAggregate
class TestTemplateSectionAggregate(AggregateTestBase):
    '''Tests for TemplateSectionAggregate.'''

    aggregate_cls = TemplateSectionAggregate
    sample_data = SEC_SAMPLE_DATA
    equality_fields = SEC_EQUALITY_FIELDS

    set_attribute_params = [
        ('title',           'Updated Section', None),
        ('default_content', 'New content',     None),
        ('content_type',    'code',            None),
        ('invalid_attr',    'value',           'INVALID_MODEL_ATTRIBUTE'),
    ]

    # ** test: rename
    def test_rename(self, aggregate):
        '''Test section rename.'''

        aggregate.rename('Action Items')
        assert aggregate.title == 'Action Items'

    # ** test: set_default_content
    def test_set_default_content(self, aggregate):
        '''Test set_default_content.'''

        aggregate.set_default_content('New default')
        assert aggregate.default_content == 'New default'

    # ** test: set_content_type
    def test_set_content_type(self, aggregate):
        '''Test set_content_type.'''

        aggregate.set_content_type('code')
        assert aggregate.content_type == 'code'


# *** standalone TableObject tests

# ** fixture: tmpl_h5_table
@pytest.fixture
def tmpl_h5_table(tmp_path: Path):
    '''Open a temporary HDF5 file and yield a live template table.'''
    h5_path = tmp_path / 'test.h5'
    h5file = tables.open_file(str(h5_path), mode='w')
    table = h5file.create_table('/', 'templates', TemplateTableObject.get_description())
    yield table
    h5file.close()


# ** fixture: tmpl_sec_h5_table
@pytest.fixture
def tmpl_sec_h5_table(tmp_path: Path):
    '''Open a temporary HDF5 file and yield a live template section table.'''
    h5_path = tmp_path / 'test_sec.h5'
    h5file = tables.open_file(str(h5_path), mode='w')
    table = h5file.create_table('/', 'sections', TemplateSectionTableObject.get_description())
    yield table
    h5file.close()


# ** test: template_table_object_round_trip
def test_template_table_object_round_trip(tmpl_h5_table):
    '''Test TemplateTableObject to_row/from_row round-trip.'''

    obj = TemplateTableObject(
        id='tmpl-001', name='Meeting Notes', description='For meetings',
        category_id='meetings', created_at='2026-01-01T00:00:00', updated_at='2026-01-01T00:00:00',
    )
    obj.to_row(tmpl_h5_table)
    tmpl_h5_table.flush()

    rows = list(tmpl_h5_table.iterrows())
    assert len(rows) == 1

    restored = TemplateTableObject.from_row(rows[0])
    assert restored.id == 'tmpl-001'
    assert restored.name == 'Meeting Notes'


# ** test: template_table_object_map_converts_empty_to_none
def test_template_table_object_map_converts_empty_to_none():
    '''Test that map() converts empty string optionals to None.'''

    obj = TemplateTableObject(
        id='t1', name='Test', description='', category_id='',
        created_at='2026-01-01T00:00:00', updated_at='2026-01-01T00:00:00',
    )
    agg = obj.map()
    assert agg.description is None
    assert agg.category_id is None


# ** test: template_section_table_object_round_trip
def test_template_section_table_object_round_trip(tmpl_sec_h5_table):
    '''Test TemplateSectionTableObject to_row/from_row round-trip.'''

    obj = TemplateSectionTableObject(
        id='tsec-001', template_id='tmpl-001', title='Agenda',
        content_type='markdown', default_content='## Agenda', position=0,
    )
    obj.to_row(tmpl_sec_h5_table)
    tmpl_sec_h5_table.flush()

    rows = list(tmpl_sec_h5_table.iterrows())
    assert len(rows) == 1

    restored = TemplateSectionTableObject.from_row(rows[0])
    assert restored.id == 'tsec-001'
    assert restored.title == 'Agenda'
    assert restored.default_content == '## Agenda'
    assert restored.position == 0
