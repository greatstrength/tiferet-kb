"""tiferet_kb Section Comment Domain Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..comment import SectionComment
from ..document import DocumentSection

# *** tests

# ** test: section_comment_derives_id_and_created_at
def test_section_comment_derives_id_and_created_at():
    '''A comment derives id and created_at and has no update timestamp.'''

    comment = SectionComment(
        document_id='doc-001',
        section_id='sec-001',
        author='ada',
        text='A note',
    )
    assert comment.id is not None and len(comment.id) == 36
    assert comment.created_at is not None
    assert comment.parent_id is None
    assert 'updated_at' not in SectionComment.model_fields
    assert 'content' not in SectionComment.model_fields
    assert 'paragraphs' not in SectionComment.model_fields
    assert 'resolved' not in SectionComment.model_fields

# ** test: section_comment_preserves_explicit_id_and_timestamp
def test_section_comment_preserves_explicit_id_and_timestamp():
    '''A caller-supplied id and created_at are kept.'''

    comment = SectionComment(
        id='cmt-001',
        document_id='doc-001',
        section_id='sec-001',
        author='ada',
        text='A note',
        parent_id='cmt-000',
        created_at='10',
    )
    assert comment.id == 'cmt-001'
    assert comment.created_at == '10'
    assert comment.parent_id == 'cmt-000'

# ** test: section_comment_rejects_extra_fields
def test_section_comment_rejects_extra_fields():
    '''A comment does not accept content, paragraphs, or a resolved flag.'''

    with pytest.raises(Exception):
        SectionComment(
            document_id='doc-001',
            section_id='sec-001',
            author='ada',
            text='A note',
            content='nope',
        )

# ** test: document_section_has_no_comment_fields
def test_document_section_has_no_comment_fields():
    '''A section is still heading, passages, and attributes.'''

    assert 'content' not in DocumentSection.model_fields
    assert 'comments' not in DocumentSection.model_fields
