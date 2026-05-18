"""tiferet_kb Markdown Parser Tests"""

# *** imports

# ** app
from ..markdown import (
    parse_paragraph_to_segments,
    reassemble_paragraph,
    parse_content_to_paragraphs,
)

# *** tests: parse_paragraph_to_segments

# ** test: parse_mixed_formatting
def test_parse_mixed_formatting():
    '''Parse a paragraph with all supported inline formats.'''

    text = 'Hello **bold** and *italic* with ~~strike~~ and `code` plus [link](http://example.com) end.'
    segments = parse_paragraph_to_segments(text)

    assert len(segments) == 11
    assert segments[0].format_type == 'plain'
    assert segments[1].format_type == 'bold'
    assert segments[1].text == 'bold'
    assert segments[3].format_type == 'italic'
    assert segments[5].format_type == 'strikethrough'
    assert segments[7].format_type == 'code'
    assert segments[9].format_type == 'link'
    assert segments[9].link_url == 'http://example.com'


# ** test: parse_plain_only
def test_parse_plain_only():
    '''A paragraph with no formatting produces a single plain segment.'''

    text = 'Just plain text, nothing special.'
    segments = parse_paragraph_to_segments(text)
    assert len(segments) == 1
    assert segments[0].format_type == 'plain'
    assert segments[0].text == text


# ** test: parse_empty_string
def test_parse_empty_string():
    '''An empty string produces no segments.'''

    segments = parse_paragraph_to_segments('')
    assert len(segments) == 0


# ** test: parse_consecutive_formatting
def test_parse_consecutive_formatting():
    '''Two formatted runs back-to-back with no plain text between.'''

    text = '**bold***italic*'
    segments = parse_paragraph_to_segments(text)
    assert len(segments) == 2
    assert segments[0].format_type == 'bold'
    assert segments[1].format_type == 'italic'


# *** tests: reassemble_paragraph

# ** test: round_trip_parse_reassemble
def test_round_trip_parse_reassemble():
    '''Parse then reassemble should produce the original markdown string.'''

    original = 'Start **bold** middle *italic* end ~~strike~~ `code` [link](http://x.com) tail.'
    segments = parse_paragraph_to_segments(original)
    reassembled = reassemble_paragraph(segments)
    assert reassembled == original


# *** tests: parse_content_to_paragraphs

# ** test: multi_paragraph_split
def test_multi_paragraph_split():
    '''Content with double-newlines splits into multiple paragraphs.'''

    content = 'First paragraph.\n\nSecond paragraph with **bold**.'
    paragraphs = parse_content_to_paragraphs(content, section_id='sec-1')

    assert len(paragraphs) == 2
    assert paragraphs[0].position == 0
    assert paragraphs[0].block_type == 'normal'
    assert paragraphs[1].position == 1
    assert paragraphs[1].segments[1].format_type == 'bold'


# ** test: quote_detection
def test_quote_detection():
    '''Lines starting with > are detected as quote block type.'''

    content = '> This is a **quoted** line.'
    paragraphs = parse_content_to_paragraphs(content, section_id='sec-1')

    assert len(paragraphs) == 1
    assert paragraphs[0].block_type == 'quote'
    # The > prefix should be stripped, leaving the formatted text.
    assert any(s.format_type == 'bold' for s in paragraphs[0].segments)


# ** test: code_block_detection
def test_code_block_detection():
    '''Triple-backtick fenced blocks are detected as code_block.'''

    content = '```python\nprint("hello")\n```'
    paragraphs = parse_content_to_paragraphs(content, section_id='sec-1')

    assert len(paragraphs) == 1
    assert paragraphs[0].block_type == 'code_block'
    assert paragraphs[0].segments[0].format_type == 'plain'
    assert 'print' in paragraphs[0].segments[0].text


# ** test: empty_content
def test_empty_content():
    '''Empty or whitespace-only content produces no paragraphs.'''

    assert parse_content_to_paragraphs('', section_id='sec-1') == []
    assert parse_content_to_paragraphs('   ', section_id='sec-1') == []


# ** test: mixed_block_types
def test_mixed_block_types():
    '''Content with normal, quote, and code blocks in sequence.'''

    content = 'Normal paragraph.\n\n> Quoted paragraph.\n\n```\ncode here\n```'
    paragraphs = parse_content_to_paragraphs(content, section_id='sec-1')

    assert len(paragraphs) == 3
    assert paragraphs[0].block_type == 'normal'
    assert paragraphs[1].block_type == 'quote'
    assert paragraphs[2].block_type == 'code_block'
