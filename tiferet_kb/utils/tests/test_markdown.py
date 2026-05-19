"""tiferet_kb Markdown Parser Tests"""

# *** imports

# ** app
from ..markdown import (
    parse_paragraph_to_segments,
    reassemble_paragraph,
    split_markdown_sections,
    join_markdown_sections,
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


# *** tests: split_markdown_sections

# ** test: split_basic_sections
def test_split_basic_sections():
    '''Split a markdown document with multiple H1 sections.'''

    content = '# Introduction\n\nSome intro text.\n\n# Details\n\nDetail content here.\n\n## Subsection\n\nSub content.'
    sections = split_markdown_sections(content)

    assert len(sections) == 2
    assert sections[0]['title'] == 'Introduction'
    assert sections[0]['content'] == 'Some intro text.'
    assert sections[1]['title'] == 'Details'
    assert '## Subsection' in sections[1]['content']


# ** test: split_single_section
def test_split_single_section():
    '''A document with one H1 produces one section.'''

    content = '# Only Section\n\nContent here.'
    sections = split_markdown_sections(content)

    assert len(sections) == 1
    assert sections[0]['title'] == 'Only Section'
    assert sections[0]['content'] == 'Content here.'


# ** test: split_empty_content
def test_split_empty_content():
    '''Empty content produces no sections.'''

    assert split_markdown_sections('') == []
    assert split_markdown_sections('   ') == []


# ** test: split_no_h1_raises
def test_split_no_h1_raises():
    '''Content not starting with H1 raises ValueError.'''

    import pytest
    with pytest.raises(ValueError):
        split_markdown_sections('No heading here.\n\nJust paragraphs.')


# ** test: split_section_no_content
def test_split_section_no_content():
    '''An H1 with no body produces a section with empty content.'''

    content = '# Empty Section\n# Next Section\n\nHas content.'
    sections = split_markdown_sections(content)

    assert len(sections) == 2
    assert sections[0]['title'] == 'Empty Section'
    assert sections[0]['content'] == ''
    assert sections[1]['title'] == 'Next Section'
    assert sections[1]['content'] == 'Has content.'


# *** tests: join_markdown_sections

# ** test: join_dict_sections
def test_join_dict_sections():
    '''Join sections from dicts back into markdown.'''

    sections = [
        {'title': 'Introduction', 'content': 'Some intro.'},
        {'title': 'Details', 'content': 'Detail content.'},
    ]
    result = join_markdown_sections(sections)

    assert result == '# Introduction\n\nSome intro.\n\n# Details\n\nDetail content.\n'


# ** test: join_empty_list
def test_join_empty_list():
    '''Joining an empty list produces an empty string.'''

    assert join_markdown_sections([]) == ''


# ** test: round_trip_split_join
def test_round_trip_split_join():
    '''Splitting then joining should produce equivalent markdown.'''

    original = '# First\n\nContent one.\n\n# Second\n\nContent two.\n'
    sections = split_markdown_sections(original)
    result = join_markdown_sections(sections)
    assert result == original


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
