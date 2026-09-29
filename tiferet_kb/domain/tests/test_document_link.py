"""tiferet_kb Document Link Domain Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...assets.core import (
    DOCUMENT_LINK_REFERENCES,
    DOCUMENT_LINK_RELATED_TO,
    DOCUMENT_LINK_SUPERSEDES,
)
from ..document import Document
from ..document_link import DocumentLink

# *** tests

# ** test: document_link_derives_id_and_timestamp
def test_document_link_derives_id_and_timestamp():
    '''A link derives its id and created_at when the caller omits them.'''

    link = DocumentLink(
        source_id='doc-001',
        target_id='doc-002',
        link_type=DOCUMENT_LINK_REFERENCES,
    )
    assert link.id
    assert link.created_at
    assert link.source_id == 'doc-001'
    assert link.target_id == 'doc-002'
    assert link.link_type == 'references'

# ** test: document_link_preserves_explicit_id
def test_document_link_preserves_explicit_id():
    '''An explicit id is kept.'''

    link = DocumentLink(
        id='link-001',
        source_id='doc-001',
        target_id='doc-002',
        link_type='cites',
        created_at='2026-01-01T00:00:00+00:00',
    )
    assert link.id == 'link-001'
    assert link.created_at == '2026-01-01T00:00:00+00:00'
    assert link.link_type == 'cites'

# ** test: document_link_strips_type_and_keeps_case
def test_document_link_strips_type_and_keeps_case():
    '''Ends are stripped. Case is not folded.'''

    stripped = DocumentLink(
        source_id='doc-001',
        target_id='doc-002',
        link_type='  references  ',
    )
    kept = DocumentLink(
        source_id='doc-001',
        target_id='doc-002',
        link_type='References',
    )
    assert stripped.link_type == 'references'
    assert kept.link_type == 'References'

# ** test: documented_type_constants
def test_documented_type_constants():
    '''The three documented names are constants, not a closed set.'''

    assert DOCUMENT_LINK_REFERENCES == 'references'
    assert DOCUMENT_LINK_SUPERSEDES == 'supersedes'
    assert DOCUMENT_LINK_RELATED_TO == 'related_to'

# ** test: document_does_not_gain_links_or_content
def test_document_does_not_gain_links_or_content():
    '''A document header does not grow a links field or a content field.'''

    assert 'links' not in Document.model_fields
    assert 'content' not in Document.model_fields

# ** test: document_link_rejects_extra_fields
def test_document_link_rejects_extra_fields():
    '''A link has no title, status, or passage.'''

    with pytest.raises(Exception):
        DocumentLink(
            source_id='doc-001',
            target_id='doc-002',
            link_type='references',
            title='not a link field',
        )
