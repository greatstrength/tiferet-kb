"""tiferet_kb Segment Domain Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..segment import TextSegment, Paragraph

# *** tests

# ** test: text_segment_auto_generates_id
def test_text_segment_auto_generates_id():
    '''Test that TextSegment auto-generates a UUID id.'''

    seg = TextSegment(position=0, text='hello')
    assert seg.id is not None and len(seg.id) == 36
    assert seg.format_type == 'plain'
    assert seg.link_url is None


# ** test: text_segment_preserves_explicit_id
def test_text_segment_preserves_explicit_id():
    '''Test that an explicit id is preserved.'''

    seg = TextSegment(id='my-seg-id', position=0, text='hello')
    assert seg.id == 'my-seg-id'


# ** test: text_segment_all_format_types
def test_text_segment_all_format_types():
    '''Test construction with each supported format type.'''

    for fmt in ('plain', 'bold', 'italic', 'strikethrough', 'code', 'link'):
        seg = TextSegment(position=0, text='test', format_type=fmt)
        assert seg.format_type == fmt


# ** test: text_segment_link_with_url
def test_text_segment_link_with_url():
    '''Test link segment carries its URL.'''

    seg = TextSegment(position=0, text='click', format_type='link', link_url='http://example.com')
    assert seg.link_url == 'http://example.com'


# ** test: paragraph_auto_generates_id
def test_paragraph_auto_generates_id():
    '''Test that Paragraph auto-generates a UUID id.'''

    para = Paragraph(section_id='sec-1', position=0)
    assert para.id is not None and len(para.id) == 36
    assert para.block_type == 'normal'
    assert para.segments == []


# ** test: paragraph_with_segments
def test_paragraph_with_segments():
    '''Test Paragraph construction with nested segments.'''

    segs = [
        TextSegment(position=0, text='Hello ', format_type='plain'),
        TextSegment(position=1, text='world', format_type='bold'),
    ]
    para = Paragraph(section_id='sec-1', position=0, block_type='quote', segments=segs)
    assert len(para.segments) == 2
    assert para.block_type == 'quote'
    assert para.segments[1].format_type == 'bold'


# ** test: paragraph_block_type_variants
def test_paragraph_block_type_variants():
    '''Test construction with each supported block type.'''

    for bt in ('normal', 'quote', 'code_block', 'list_item'):
        para = Paragraph(section_id='sec-1', position=0, block_type=bt)
        assert para.block_type == bt


# ** test: paragraph_rejects_extra_fields
def test_paragraph_rejects_extra_fields():
    '''Test that DomainObject extra=forbid rejects unknown fields.'''

    with pytest.raises(Exception):
        Paragraph(section_id='sec-1', position=0, unknown_field='bad')
