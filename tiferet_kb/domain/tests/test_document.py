"""tiferet_kb Document Domain Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..document import Document, DocumentSection

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
