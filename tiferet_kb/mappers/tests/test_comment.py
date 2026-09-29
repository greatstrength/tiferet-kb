"""tiferet_kb Section Comment Mapper Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
import tables

# ** app
from ..comment import SectionCommentAggregate, SectionCommentTableObject

# *** fixtures

# ** fixture: comment_h5_table
@pytest.fixture
def comment_h5_table(tmp_path: Path):
    '''Open a temporary HDF5 file and yield a live section-comment table.'''

    h5_path = tmp_path / 'test.h5'
    h5file = tables.open_file(str(h5_path), mode='w')
    table = h5file.create_table('/', 'section_comments', SectionCommentTableObject.get_description())
    yield table
    h5file.close()

# *** tests

# ** test: section_comment_table_object_round_trip
def test_section_comment_table_object_round_trip(comment_h5_table):
    '''A comment row round-trips, and an absent parent id reads back as absent.'''

    comment = SectionCommentAggregate(
        id='cmt-001',
        document_id='doc-001',
        section_id='sec-001',
        author='ada',
        text='# not a heading',
        created_at='2026-01-01T00:00:00+00:00',
    )
    obj = SectionCommentTableObject.from_model(comment)
    assert obj.parent_id is None
    obj.to_row(comment_h5_table)
    comment_h5_table.flush()

    restored = SectionCommentTableObject.from_row(list(comment_h5_table.iterrows())[0]).map()
    assert restored.id == 'cmt-001'
    assert restored.text == '# not a heading'
    assert restored.parent_id is None
    assert 'content' not in type(restored).model_fields

# ** test: section_comment_table_object_stores_parent_id
def test_section_comment_table_object_stores_parent_id(comment_h5_table):
    '''A parent id is stored and read back on the same row.'''

    comment = SectionCommentAggregate(
        id='cmt-002',
        document_id='doc-001',
        section_id='sec-001',
        author='ada',
        text='a reply',
        parent_id='cmt-001',
        created_at='2026-01-02T00:00:00+00:00',
    )
    SectionCommentTableObject.from_model(comment).to_row(comment_h5_table)
    comment_h5_table.flush()

    restored = SectionCommentTableObject.from_row(list(comment_h5_table.iterrows())[0]).map()
    assert restored.parent_id == 'cmt-001'
