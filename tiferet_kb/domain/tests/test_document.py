"""tiferet_kb Document Domain Tests"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from ..document import Document, DocumentSection, SectionRevision
from ..segment import Paragraph, TextSegment
from ...mappers.document import DocumentSectionAggregate
from ...utils.markdown import render_section

# *** tests

# ** test: document_auto_generates_id_and_timestamps
def test_document_auto_generates_id_and_timestamps():
    '''Test that Document auto-generates id, status, and timestamps.'''

    doc = Document(title='Test Doc')
    assert doc.id is not None and len(doc.id) == 36  # UUID format
    assert doc.status == 'draft'
    assert doc.created_at is not None
    assert doc.updated_at is not None

# ** test: document_preserves_explicit_id
def test_document_preserves_explicit_id():
    '''Test that an explicit id is preserved.'''

    doc = Document(id='my-custom-id', title='Test Doc')
    assert doc.id == 'my-custom-id'

# ** test: document_optional_fields_default_none
def test_document_optional_fields_default_none():
    '''Test that optional FK fields default to None.'''

    doc = Document(title='Test Doc')
    assert doc.category_id is None
    assert doc.template_id is None
    assert doc.folder_id is None
    assert doc.sections == []

# ** test: document_get_section
def test_document_get_section():
    '''Test get_section returns the correct section by position.'''

    section = DocumentSection(document_id='doc1', title='Intro', position=0)
    doc = Document(title='Test Doc', sections=[section])
    assert doc.get_section(0) is not None
    assert doc.get_section(0).title == 'Intro'
    assert doc.get_section(1) is None

# ** test: document_section_count
def test_document_section_count():
    '''Test section_count returns the correct count.'''

    doc = Document(title='Test Doc')
    assert doc.section_count() == 0

    section = DocumentSection(document_id='doc1', title='Intro', position=0)
    doc2 = Document(title='Test Doc', sections=[section])
    assert doc2.section_count() == 1

# ** test: document_section_auto_generates_defaults
def test_document_section_auto_generates_defaults():
    '''Test that DocumentSection auto-generates id and timestamps.'''

    section = DocumentSection(document_id='doc1', title='Intro', position=0)
    assert section.id is not None and len(section.id) == 36
    assert section.created_at is not None
    assert section.heading_level == 2
    assert section.content_type == 'markdown'
    assert section.paragraphs == []

# ** test: document_rejects_extra_fields
def test_document_rejects_extra_fields():
    '''Test that DomainObject extra=forbid rejects unknown fields.'''

    with pytest.raises(Exception):
        Document(title='Test', unknown_field='bad')

# ** test: section_accepts_content_string
def test_section_accepts_content_string():
    '''A content string constructs a section and renders back.'''

    section = DocumentSectionAggregate(
        id='fact-1',
        document_id='ns-1',
        title='user prefers',
        content='user prefers Python',
    )

    assert section.position == 0
    assert section.paragraphs
    assert section.content == 'user prefers Python'
    assert 'content' not in section.model_dump()
    assert render_section(section) == section.content
    assert not render_section(section).endswith('\n')
    assert '# user prefers' not in render_section(section)

# ** test: section_paragraphs_win_over_content
def test_section_paragraphs_win_over_content():
    '''Non-empty paragraphs are kept when content is also passed.'''

    kept = Paragraph(
        id='para-1',
        section_id='fact-1',
        position=0,
        block_type='normal',
        segments=[TextSegment(id='seg-1', position=0, text='stored passage', format_type='plain')],
    )
    section = DocumentSection(
        id='fact-1',
        document_id='ns-1',
        title='user prefers',
        paragraphs=[kept],
        content='user prefers Python',
    )

    assert section.paragraphs[0].segments[0].text == 'stored passage'
    assert section.content == 'stored passage'

# ** test: section_rejects_non_string_content
def test_section_rejects_non_string_content():
    '''A non-string content value is a validation error.'''

    with pytest.raises(ValidationError):
        DocumentSection(
            id='fact-1',
            document_id='ns-1',
            title='user prefers',
            content=12,
        )

# ** test: section_rejects_undeclared_field
def test_section_rejects_undeclared_field():
    '''An undeclared field other than consumed content still fails.'''

    with pytest.raises(ValidationError):
        DocumentSection(
            id='fact-1',
            document_id='ns-1',
            title='user prefers',
            content='user prefers Python',
            unknown_field='bad',
        )

# ** test: section_empty_content_renders_empty
def test_section_empty_content_renders_empty():
    '''Missing or empty content stores no paragraphs.'''

    missing = DocumentSection(document_id='ns-1', title='empty')
    empty = DocumentSection(document_id='ns-1', title='empty', content='')

    assert missing.position == 0
    assert missing.paragraphs == []
    assert missing.content == ''
    assert empty.content == ''
    assert render_section(empty) == ''

# ** test: document_visibility_defaults_public
def test_document_visibility_defaults_public():
    '''A document with no visibility reads as public and has no owner.'''

    doc = Document(title='Test Doc')
    assert doc.visibility == 'public'
    assert doc.owner_id is None

# ** test: document_blank_visibility_reads_public
def test_document_blank_visibility_reads_public():
    '''Empty or whitespace visibility and owner read as public and absent.'''

    doc = Document.model_validate({
        'title': 'Test Doc',
        'visibility': '',
        'owner_id': '   ',
    })
    assert doc.visibility == 'public'
    assert doc.owner_id is None

# ** test: document_stores_visibility_and_owner
def test_document_stores_visibility_and_owner():
    '''An explicit visibility and owner are kept, and visibility is never absent.'''

    doc = Document(title='Test Doc', visibility='private', owner_id='owner-1')
    assert doc.visibility == 'private'
    assert doc.owner_id == 'owner-1'
    assert doc.visibility is not None

# ** test: matches_paragraphs_ignores_identifiers_and_empty_links
def test_matches_paragraphs_ignores_identifiers_and_empty_links():
    '''Identifiers are ignored, and an absent link URL equals an empty one.'''

    stored = Paragraph(
        id='stored-p',
        section_id='sec-1',
        position=0,
        block_type='normal',
        segments=[TextSegment(
            id='stored-s',
            position=0,
            text='Hello',
            format_type='link',
            link_url=None,
        )],
    )
    parsed = Paragraph(
        id='parsed-p',
        section_id='other',
        position=0,
        block_type='normal',
        segments=[TextSegment(
            id='parsed-s',
            position=0,
            text='Hello',
            format_type='link',
            link_url='',
        )],
    )
    section = DocumentSection(
        document_id='doc-1',
        title='Intro',
        position=0,
        paragraphs=[stored],
    )

    assert section.matches_paragraphs([parsed]) is True

# ** test: matches_paragraphs_detects_passage_differences
def test_matches_paragraphs_detects_passage_differences():
    '''Order, position, block type, text, and format are differences.'''

    left = Paragraph(
        id='p',
        section_id='sec-1',
        position=0,
        block_type='normal',
        segments=[TextSegment(id='s', position=0, text='Alpha', format_type='plain')],
    )
    section = DocumentSection(
        document_id='doc-1',
        title='Intro',
        position=0,
        paragraphs=[left],
    )
    different_text = left.model_copy(deep=True)
    different_text.segments[0].text = 'Beta'

    assert section.matches_paragraphs([different_text]) is False
    assert section.matches_paragraphs([]) is False

# ** test: section_revision_has_no_content_string
def test_section_revision_has_no_content_string():
    '''A revision is the paragraph model, not a content string or an author.'''

    revision = SectionRevision(
        document_id='doc-1',
        section_id='sec-1',
        number=1,
        title='Intro',
        content_type='markdown',
        created_at='2026-01-01T00:00:00+00:00',
    )

    assert 'content' not in SectionRevision.model_fields
    assert 'author' not in SectionRevision.model_fields
    assert revision.paragraphs == []
    with pytest.raises(Exception):
        SectionRevision(
            document_id='doc-1',
            section_id='sec-1',
            number=0,
            title='Intro',
            content_type='markdown',
        )
