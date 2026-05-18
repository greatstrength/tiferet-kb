"""tiferet_kb Segment Mapper Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
import tables

# ** app
from ..segment import HybridSegmentTableObject
from ..document import DocumentSectionAggregate, DocumentSectionNodeObject
from ...domain.segment import TextSegment, Paragraph

# *** tests: HybridSegmentTableObject

# ** fixture: segment_h5_table
@pytest.fixture
def segment_h5_table(tmp_path: Path):
    '''Open a temporary HDF5 file and yield a live hybrid segment table.'''

    h5_path = tmp_path / 'test_segments.h5'
    h5file = tables.open_file(str(h5_path), mode='w')
    table = h5file.create_table('/', 'segments', HybridSegmentTableObject.get_description())
    yield table
    h5file.close()


# ** test: hybrid_segment_round_trip_plain
def test_hybrid_segment_round_trip_plain(segment_h5_table):
    '''Test to_row/from_row round-trip for a plain segment.'''

    obj = HybridSegmentTableObject(
        paragraph_id='para-001', paragraph_position=0, block_type='normal',
        id='seg-001', position=0, text='Hello world', format_type='plain',
    )
    obj.to_row(segment_h5_table)
    segment_h5_table.flush()

    rows = list(segment_h5_table.iterrows())
    assert len(rows) == 1

    restored = HybridSegmentTableObject.from_row(rows[0])
    assert restored.paragraph_id == 'para-001'
    assert restored.block_type == 'normal'
    assert restored.id == 'seg-001'
    assert restored.text == 'Hello world'
    assert restored.format_type == 'plain'


# ** test: hybrid_segment_round_trip_link
def test_hybrid_segment_round_trip_link(segment_h5_table):
    '''Test to_row/from_row round-trip for a link segment with URL.'''

    obj = HybridSegmentTableObject(
        paragraph_id='para-002', paragraph_position=1, block_type='quote',
        id='seg-002', position=0, text='Tiferet', format_type='link',
        link_url='https://github.com/greatstrength/tiferet',
    )
    obj.to_row(segment_h5_table)
    segment_h5_table.flush()

    rows = list(segment_h5_table.iterrows())
    restored = HybridSegmentTableObject.from_row(rows[0])
    assert restored.format_type == 'link'
    assert restored.link_url == 'https://github.com/greatstrength/tiferet'


# ** test: hybrid_segment_map_to_text_segment
def test_hybrid_segment_map_to_text_segment():
    '''Test map() produces a TextSegment, stripping paragraph-level fields.'''

    obj = HybridSegmentTableObject(
        paragraph_id='para-001', paragraph_position=0, block_type='normal',
        id='seg-001', position=0, text='Hello', format_type='bold',
    )
    seg = obj.map()

    assert isinstance(seg, TextSegment)
    assert seg.id == 'seg-001'
    assert seg.text == 'Hello'
    assert seg.format_type == 'bold'
    assert seg.link_url is None
    # Paragraph-level fields should not be on TextSegment.
    assert not hasattr(seg, 'paragraph_id')


# ** test: hybrid_segment_map_empty_link_url_to_none
def test_hybrid_segment_map_empty_link_url_to_none():
    '''Test map() converts empty link_url to None.'''

    obj = HybridSegmentTableObject(
        paragraph_id='p', paragraph_position=0, block_type='normal',
        id='s', position=0, text='test', format_type='plain', link_url='',
    )
    seg = obj.map()
    assert seg.link_url is None


# *** tests: DocumentSectionNodeObject

# ** test: section_node_object_to_attrs_excludes_paragraphs
def test_section_node_object_to_attrs_excludes_paragraphs():
    '''Test that to_attrs excludes id, document_id, and paragraphs.'''

    section = DocumentSectionAggregate(
        document_id='doc-1', title='Intro', position=0,
        heading_level=2, icon='book', content_type='markdown',
    )
    node_obj = DocumentSectionNodeObject.from_model(section)
    attrs = node_obj.to_attrs()

    assert 'title' in attrs
    assert 'heading_level' in attrs
    assert 'position' in attrs
    assert 'id' not in attrs
    assert 'document_id' not in attrs
    assert 'paragraphs' not in attrs


# ** test: section_node_object_round_trip
def test_section_node_object_round_trip():
    '''Test from_model -> to_attrs -> from_attrs -> map round-trip.'''

    section = DocumentSectionAggregate(
        id='sec-1', document_id='doc-1', title='Intro',
        heading_level=3, icon='star', content_type='markdown', position=0,
    )
    node_obj = DocumentSectionNodeObject.from_model(section)
    attrs = node_obj.to_attrs()

    restored_obj = DocumentSectionNodeObject.from_attrs(attrs, id='sec-1', document_id='doc-1')
    restored = restored_obj.map()

    assert restored.id == 'sec-1'
    assert restored.document_id == 'doc-1'
    assert restored.title == 'Intro'
    assert restored.heading_level == 3
    assert restored.icon == 'star'


# ** test: section_node_object_none_icon_converts_to_empty
def test_section_node_object_none_icon_converts_to_empty():
    '''Test from_model converts None icon to empty string for HDF5 attrs.'''

    section = DocumentSectionAggregate(
        document_id='doc-1', title='Intro', position=0, icon=None,
    )
    node_obj = DocumentSectionNodeObject.from_model(section)
    assert node_obj.icon == ''


# *** tests: DocumentSectionAggregate mutations

# ** test: aggregate_set_paragraphs
def test_aggregate_set_paragraphs():
    '''Test set_paragraphs mutation.'''

    section = DocumentSectionAggregate(
        document_id='doc-1', title='Intro', position=0,
    )
    old_updated = section.updated_at
    paragraphs = [
        Paragraph(section_id=section.id, position=0, segments=[
            TextSegment(position=0, text='test', format_type='bold'),
        ]),
    ]
    section.set_paragraphs(paragraphs)

    assert len(section.paragraphs) == 1
    assert section.paragraphs[0].segments[0].format_type == 'bold'
    assert section.updated_at != old_updated


# ** test: aggregate_set_heading_level
def test_aggregate_set_heading_level():
    '''Test set_heading_level mutation.'''

    section = DocumentSectionAggregate(
        document_id='doc-1', title='Intro', position=0,
    )
    section.set_heading_level(3)
    assert section.heading_level == 3


# ** test: aggregate_set_icon
def test_aggregate_set_icon():
    '''Test set_icon mutation.'''

    section = DocumentSectionAggregate(
        document_id='doc-1', title='Intro', position=0,
    )
    section.set_icon('star')
    assert section.icon == 'star'

    section.set_icon(None)
    assert section.icon is None
