"""tiferet_kb Document Link Mapper Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
import tables

# ** app
from ..document import DocumentTableObject
from ..document_link import DocumentLinkAggregate, DocumentLinkTableObject

# *** fixtures

# ** fixture: link_h5_table
@pytest.fixture
def link_h5_table(tmp_path: Path):
    '''Open a temporary HDF5 file and yield a live link table.'''

    h5_path = tmp_path / 'links.h5'
    h5file = tables.open_file(str(h5_path), mode='w')
    table = h5file.create_table('/', 'document_links', DocumentLinkTableObject.get_description())
    yield table
    h5file.close()

# *** tests

# ** test: widths_follow_header_table
def test_widths_follow_header_table():
    '''Link columns use the aligned header widths, not a new scheme.'''

    header = DocumentTableObject._H5_TYPES
    link = DocumentLinkTableObject._H5_TYPES
    assert link['id'].itemsize == header['id'].itemsize
    assert link['source_id'].itemsize == header['id'].itemsize
    assert link['target_id'].itemsize == header['id'].itemsize
    assert link['link_type'].itemsize == header['title'].itemsize
    assert link['created_at'].itemsize == header['created_at'].itemsize

# ** test: round_trip
def test_round_trip(link_h5_table):
    '''A link row survives to_row and from_row unchanged.'''

    obj = DocumentLinkTableObject(
        id='link-001',
        source_id='doc-001',
        target_id='doc-002',
        link_type='references',
        created_at='2026-01-01T00:00:00+00:00',
    )
    obj.to_row(link_h5_table)
    link_h5_table.flush()

    restored = DocumentLinkTableObject.from_row(list(link_h5_table.iterrows())[0])
    assert restored.id == 'link-001'
    assert restored.source_id == 'doc-001'
    assert restored.target_id == 'doc-002'
    assert restored.link_type == 'references'
    assert restored.created_at == '2026-01-01T00:00:00+00:00'

# ** test: map_and_from_model
def test_map_and_from_model():
    '''The table object maps to the aggregate and back.'''

    link = DocumentLinkAggregate(
        id='link-001',
        source_id='doc-001',
        target_id='doc-002',
        link_type='supersedes',
        created_at='2026-01-02T00:00:00+00:00',
    )
    obj = DocumentLinkTableObject.from_model(link)
    restored = obj.map()
    assert restored.id == link.id
    assert restored.source_id == link.source_id
    assert restored.target_id == link.target_id
    assert restored.link_type == link.link_type
    assert restored.created_at == link.created_at

# ** test: value_fits_rejects_clip_and_null
def test_value_fits_rejects_clip_and_null():
    '''A value that would be clipped, including a null byte, does not fit.'''

    width = DocumentLinkTableObject.type_width()
    assert DocumentLinkTableObject.value_fits('x' * width, width) is True
    assert DocumentLinkTableObject.value_fits('x' * (width + 1), width) is False
    assert DocumentLinkTableObject.value_fits('bad\x00type', width) is False
