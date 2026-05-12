"""tiferet_kb Document Mapper Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
import tables

# ** app
from ..document import (
    DocumentAggregate,
    DocumentSectionAggregate,
    DocumentTableObject,
    DocumentSectionTableObject,
)
from .settings import AggregateTestBase

# *** constants

# ** constant: doc_sample_data
DOC_SAMPLE_DATA = {
    'id': 'doc-001',
    'title': 'Test Document',
    'category_id': 'meeting-notes',
    'template_id': None,
    'folder_id': None,
    'status': 'draft',
    'created_at': '2026-01-01T00:00:00+00:00',
    'updated_at': '2026-01-01T00:00:00+00:00',
}

# ** constant: doc_equality_fields
DOC_EQUALITY_FIELDS = ['id', 'title', 'status', 'created_at']

# ** constant: section_sample_data
SECTION_SAMPLE_DATA = {
    'id': 'sec-001',
    'document_id': 'doc-001',
    'title': 'Introduction',
    'content_type': 'markdown',
    'content': '# Hello World',
    'position': 0,
    'created_at': '2026-01-01T00:00:00+00:00',
    'updated_at': '2026-01-01T00:00:00+00:00',
}

# ** constant: section_equality_fields
SECTION_EQUALITY_FIELDS = ['id', 'document_id', 'title', 'content_type', 'content', 'position']


# *** classes

# ** class: TestDocumentAggregate
class TestDocumentAggregate(AggregateTestBase):
    '''Tests for DocumentAggregate.'''

    aggregate_cls = DocumentAggregate
    sample_data = DOC_SAMPLE_DATA
    equality_fields = DOC_EQUALITY_FIELDS

    set_attribute_params = [
        ('title',       'Updated Title',  None),
        ('status',      'published',      None),
        ('invalid_attr', 'value',         'INVALID_MODEL_ATTRIBUTE'),
    ]

    # *** domain-specific mutation tests

    # ** test: rename
    def test_rename(self, aggregate):
        '''Test the rename mutation updates title and timestamp.'''

        old_updated = aggregate.updated_at
        aggregate.rename('New Title')
        assert aggregate.title == 'New Title'
        assert aggregate.updated_at != old_updated

    # ** test: set_status
    def test_set_status(self, aggregate):
        '''Test the set_status mutation.'''

        aggregate.set_status('published')
        assert aggregate.status == 'published'

    # ** test: set_folder
    def test_set_folder(self, aggregate):
        '''Test the set_folder mutation.'''

        aggregate.set_folder('folder-123')
        assert aggregate.folder_id == 'folder-123'

    # ** test: set_category
    def test_set_category(self, aggregate):
        '''Test the set_category mutation.'''

        aggregate.set_category('design-docs')
        assert aggregate.category_id == 'design-docs'


# ** class: TestDocumentSectionAggregate
class TestDocumentSectionAggregate(AggregateTestBase):
    '''Tests for DocumentSectionAggregate.'''

    aggregate_cls = DocumentSectionAggregate
    sample_data = SECTION_SAMPLE_DATA
    equality_fields = SECTION_EQUALITY_FIELDS

    set_attribute_params = [
        ('title',        'Updated Section', None),
        ('content',      'New content',     None),
        ('content_type', 'code',            None),
        ('invalid_attr', 'value',           'INVALID_MODEL_ATTRIBUTE'),
    ]

    # *** domain-specific mutation tests

    # ** test: rename
    def test_rename(self, aggregate):
        '''Test section rename updates title and timestamp.'''

        old_updated = aggregate.updated_at
        aggregate.rename('Updated Section')
        assert aggregate.title == 'Updated Section'
        assert aggregate.updated_at != old_updated

    # ** test: set_content
    def test_set_content(self, aggregate):
        '''Test set_content mutation.'''

        aggregate.set_content('New content here')
        assert aggregate.content == 'New content here'

    # ** test: set_content_type
    def test_set_content_type(self, aggregate):
        '''Test set_content_type mutation.'''

        aggregate.set_content_type('code')
        assert aggregate.content_type == 'code'


# *** standalone TableObject tests

# ** fixture: doc_h5_table
@pytest.fixture
def doc_h5_table(tmp_path: Path):
    '''Open a temporary HDF5 file and yield a live document table.'''
    h5_path = tmp_path / 'test.h5'
    h5file = tables.open_file(str(h5_path), mode='w')
    table = h5file.create_table('/', 'documents', DocumentTableObject.get_description())
    yield table
    h5file.close()


# ** fixture: section_h5_table
@pytest.fixture
def section_h5_table(tmp_path: Path):
    '''Open a temporary HDF5 file and yield a live section table.'''
    h5_path = tmp_path / 'test_sections.h5'
    h5file = tables.open_file(str(h5_path), mode='w')
    table = h5file.create_table('/', 'sections', DocumentSectionTableObject.get_description())
    yield table
    h5file.close()


# ** test: document_table_object_round_trip
def test_document_table_object_round_trip(doc_h5_table):
    '''Test DocumentTableObject to_row/from_row round-trip.'''

    obj = DocumentTableObject(
        id='doc-001', title='Test Doc', category_id='notes',
        status='draft', created_at='2026-01-01T00:00:00', updated_at='2026-01-01T00:00:00',
    )
    obj.to_row(doc_h5_table)
    doc_h5_table.flush()

    rows = list(doc_h5_table.iterrows())
    assert len(rows) == 1

    restored = DocumentTableObject.from_row(rows[0])
    assert restored.id == 'doc-001'
    assert restored.title == 'Test Doc'


# ** test: document_table_object_map_converts_empty_to_none
def test_document_table_object_map_converts_empty_to_none():
    '''Test that map() converts empty string FKs to None.'''

    obj = DocumentTableObject(
        id='doc-001', title='Test', category_id='', template_id='', folder_id='',
        status='draft', created_at='2026-01-01T00:00:00', updated_at='2026-01-01T00:00:00',
    )
    agg = obj.map()
    assert agg.category_id is None
    assert agg.template_id is None
    assert agg.folder_id is None


# ** test: document_table_object_from_model_converts_none_to_empty
def test_document_table_object_from_model_converts_none_to_empty():
    '''Test that from_model() converts None FKs to empty strings for HDF5.'''

    agg = DocumentAggregate(**DOC_SAMPLE_DATA)
    obj = DocumentTableObject.from_model(agg)
    assert obj.template_id == ''
    assert obj.folder_id == ''


# ** test: section_table_object_round_trip
def test_section_table_object_round_trip(section_h5_table):
    '''Test DocumentSectionTableObject to_row/from_row round-trip.'''

    obj = DocumentSectionTableObject(
        id='sec-001', document_id='doc-001', title='Intro',
        content_type='markdown', content='# Hello', position=0,
        created_at='2026-01-01T00:00:00', updated_at='2026-01-01T00:00:00',
    )
    obj.to_row(section_h5_table)
    section_h5_table.flush()

    rows = list(section_h5_table.iterrows())
    assert len(rows) == 1

    restored = DocumentSectionTableObject.from_row(rows[0])
    assert restored.id == 'sec-001'
    assert restored.title == 'Intro'
    assert restored.content == '# Hello'
    assert restored.position == 0
