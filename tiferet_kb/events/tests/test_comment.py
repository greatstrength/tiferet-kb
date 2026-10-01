"""tiferet_kb Section Comment Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock
from tiferet_h5.utils import H5Client

# ** app
from tiferet.assets import TiferetError
from tiferet.events import DomainEvent

from ... import a
from ...interfaces.document import DocumentService
from ...mappers.comment import SectionCommentAggregate
from ...mappers.document import DocumentAggregate, DocumentSectionAggregate
from ...repos.document import DocumentH5Repository
from ..comment import AddSectionComment, ListSectionComments, RemoveSectionComment
from ..document import AddDocumentSection
from ..markdown import ExportDocumentMarkdown, ImportMarkdownDocument

# *** fixtures

# ** fixture: mock_document_service
@pytest.fixture
def mock_document_service() -> DocumentService:
    '''Mock DocumentService for comment event tests.'''
    return mock.Mock(spec=DocumentService)

# ** fixture: doc_repo
@pytest.fixture
def doc_repo(tmp_path) -> DocumentH5Repository:
    '''A document repository on a temporary HDF5 file.'''
    return DocumentH5Repository(h5_file=str(tmp_path / 'comments.h5'))

# *** tests

# ** test: add_section_comment_success
def test_add_section_comment_success(mock_document_service):
    '''A successful add returns text and does not invent content or paragraphs.'''

    section = DocumentSectionAggregate(
        id='sec-001',
        document_id='doc-001',
        title='Intro',
        position=0,
        created_at='2026-01-01T00:00:00+00:00',
        updated_at='2026-01-01T00:00:00+00:00',
    )
    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = [section]
    mock_document_service.add_comment.return_value = True

    result = DomainEvent.handle(
        AddSectionComment,
        dependencies={'document_service': mock_document_service},
        document_id='doc-001',
        section_id='sec-001',
        author='  ada  ',
        text='  # heading **bold**  ',
        id='cmt-001',
        created_at='10',
    )

    assert result.id == 'cmt-001'
    assert result.author == 'ada'
    assert result.text == '# heading **bold**'
    assert result.parent_id is None
    assert result.created_at == '10'
    assert 'content' not in type(result).model_fields
    assert 'paragraphs' not in type(result).model_fields
    assert 'updated_at' not in type(result).model_fields
    stored = mock_document_service.add_comment.call_args.args[0]
    assert stored.text == '# heading **bold**'

# ** test: add_section_comment_missing_document
def test_add_section_comment_missing_document(mock_document_service):
    '''Add on a missing document raises and writes no row.'''

    mock_document_service.exists.return_value = False

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            AddSectionComment,
            dependencies={'document_service': mock_document_service},
            document_id='missing',
            section_id='sec-001',
            author='ada',
            text='a note',
        )
    assert exc_info.value.error_code == a.errors.KB_DOCUMENT_NOT_FOUND_ID
    mock_document_service.add_comment.assert_not_called()

# ** test: add_section_comment_missing_section
def test_add_section_comment_missing_section(mock_document_service):
    '''Add on a missing section raises and writes no row.'''

    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = []

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            AddSectionComment,
            dependencies={'document_service': mock_document_service},
            document_id='doc-001',
            section_id='missing',
            author='ada',
            text='a note',
        )
    assert exc_info.value.error_code == a.errors.KB_DOCUMENT_SECTION_NOT_FOUND_ID
    mock_document_service.add_comment.assert_not_called()

# ** test: add_section_comment_rejects_empty_and_overlong
@pytest.mark.parametrize('author,text', [
    ('   ', 'a note'),
    ('ada', '   '),
    (None, 'a note'),
    ('ada', None),
    ('a' * 513, 'a note'),
    ('ada', 't' * 8193),
])
def test_add_section_comment_rejects_empty_and_overlong(mock_document_service, author, text):
    '''Empty or over-long author or text is rejected and not stored.'''

    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = [
        DocumentSectionAggregate(
            id='sec-001', document_id='doc-001', title='Intro', position=0,
            created_at='2026-01-01T00:00:00+00:00', updated_at='2026-01-01T00:00:00+00:00',
        ),
    ]

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            AddSectionComment,
            dependencies={'document_service': mock_document_service},
            document_id='doc-001',
            section_id='sec-001',
            author=author,
            text=text,
        )
    assert exc_info.value.error_code == a.errors.KB_INVALID_SECTION_COMMENT_ID
    mock_document_service.add_comment.assert_not_called()

# ** test: add_section_comment_rejects_bad_parent
def test_add_section_comment_rejects_bad_parent(mock_document_service):
    '''A missing parent, a cross-section parent, or a self parent is rejected.'''

    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = [
        DocumentSectionAggregate(
            id='sec-001', document_id='doc-001', title='Intro', position=0,
            created_at='2026-01-01T00:00:00+00:00', updated_at='2026-01-01T00:00:00+00:00',
        ),
    ]
    mock_document_service.list_comments.return_value = []

    for parent_id in ('missing', 'cmt-self'):
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                AddSectionComment,
                dependencies={'document_service': mock_document_service},
                document_id='doc-001',
                section_id='sec-001',
                author='ada',
                text='a note',
                id='cmt-self',
                parent_id=parent_id,
            )
        assert exc_info.value.error_code == a.errors.KB_INVALID_SECTION_COMMENT_ID
    mock_document_service.add_comment.assert_not_called()

# ** test: add_section_comment_accepts_reply_to_reply
def test_add_section_comment_accepts_reply_to_reply(mock_document_service):
    '''A parent id that names a comment on the same section is stored, including a reply.'''

    parent = SectionCommentAggregate(
        id='cmt-parent',
        document_id='doc-001',
        section_id='sec-001',
        author='ada',
        text='parent',
        parent_id='cmt-root',
        created_at='2026-01-01T00:00:00+00:00',
    )
    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = [
        DocumentSectionAggregate(
            id='sec-001', document_id='doc-001', title='Intro', position=0,
            created_at='2026-01-01T00:00:00+00:00', updated_at='2026-01-01T00:00:00+00:00',
        ),
    ]
    mock_document_service.list_comments.return_value = [parent]
    mock_document_service.add_comment.return_value = True

    result = DomainEvent.handle(
        AddSectionComment,
        dependencies={'document_service': mock_document_service},
        document_id='doc-001',
        section_id='sec-001',
        author='grace',
        text='reply',
        parent_id='cmt-parent',
    )
    assert result.parent_id == 'cmt-parent'

# ** test: add_section_comment_duplicate_does_not_replace
def test_add_section_comment_duplicate_does_not_replace(mock_document_service):
    '''Adding an id that already exists raises and does not ask for a replacement write.'''

    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = [
        DocumentSectionAggregate(
            id='sec-001', document_id='doc-001', title='Intro', position=0,
            created_at='2026-01-01T00:00:00+00:00', updated_at='2026-01-01T00:00:00+00:00',
        ),
    ]
    mock_document_service.add_comment.return_value = False

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            AddSectionComment,
            dependencies={'document_service': mock_document_service},
            document_id='doc-001',
            section_id='sec-001',
            author='ada',
            text='replacement',
            id='cmt-001',
        )
    assert exc_info.value.error_code == a.errors.KB_SECTION_COMMENT_ALREADY_EXISTS_ID
    mock_document_service.add_comment.assert_called_once()

# ** test: list_section_comments_missing_section_is_not_empty
def test_list_section_comments_missing_section_is_not_empty(mock_document_service):
    '''List on a missing section raises rather than returning an empty list.'''

    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = []

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            ListSectionComments,
            dependencies={'document_service': mock_document_service},
            document_id='doc-001',
            section_id='missing',
        )
    assert exc_info.value.error_code == a.errors.KB_DOCUMENT_SECTION_NOT_FOUND_ID
    mock_document_service.list_comments.assert_not_called()

# ** test: list_section_comments_empty
def test_list_section_comments_empty(mock_document_service):
    '''An existing section with no comments returns an empty list.'''

    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = [
        DocumentSectionAggregate(
            id='sec-001', document_id='doc-001', title='Intro', position=0,
            created_at='2026-01-01T00:00:00+00:00', updated_at='2026-01-01T00:00:00+00:00',
        ),
    ]
    mock_document_service.list_comments.return_value = []

    result = DomainEvent.handle(
        ListSectionComments,
        dependencies={'document_service': mock_document_service},
        document_id='doc-001',
        section_id='sec-001',
    )
    assert result == []

# ** test: list_section_comments_is_flat
def test_list_section_comments_is_flat(mock_document_service):
    '''List returns the service list unchanged, with each item's own parent id.'''

    reply = SectionCommentAggregate(
        id='cmt-2',
        document_id='doc-001',
        section_id='sec-001',
        author='ada',
        text='reply',
        parent_id='cmt-1',
        created_at='2026-01-02T00:00:00+00:00',
    )
    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = [
        DocumentSectionAggregate(
            id='sec-001', document_id='doc-001', title='Intro', position=0,
            created_at='2026-01-01T00:00:00+00:00', updated_at='2026-01-01T00:00:00+00:00',
        ),
    ]
    mock_document_service.list_comments.return_value = [reply]

    result = DomainEvent.handle(
        ListSectionComments,
        dependencies={'document_service': mock_document_service},
        document_id='doc-001',
        section_id='sec-001',
    )
    assert result == [reply]
    assert result[0].parent_id == 'cmt-1'
    assert 'replies' not in type(result[0]).model_fields

# ** test: remove_section_comment_unknown_returns_id
def test_remove_section_comment_unknown_returns_id(mock_document_service):
    '''Remove of an unknown id returns that id and raises nothing.'''

    mock_document_service.delete_comment.return_value = None

    result = DomainEvent.handle(
        RemoveSectionComment,
        dependencies={'document_service': mock_document_service},
        id='missing',
    )
    assert result == 'missing'

# ** test: remove_section_comment_with_replies
def test_remove_section_comment_with_replies(mock_document_service):
    '''Remove of a comment that still has a reply raises and deletes nothing.'''

    mock_document_service.delete_comment.return_value = False

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            RemoveSectionComment,
            dependencies={'document_service': mock_document_service},
            id='cmt-1',
        )
    assert exc_info.value.error_code == a.errors.KB_SECTION_COMMENT_HAS_REPLIES_ID

# ** test: events_are_exported
def test_events_are_exported():
    '''The three comment events are exported from tiferet_kb.events.'''

    from tiferet_kb.events import (
        AddSectionComment as ExportedAdd,
        ListSectionComments as ExportedList,
        RemoveSectionComment as ExportedRemove,
    )
    assert ExportedAdd is AddSectionComment
    assert ExportedList is ListSectionComments
    assert ExportedRemove is RemoveSectionComment

# ** test: comment_round_trip_does_not_touch_passages_or_export
def test_comment_round_trip_does_not_touch_passages_or_export(doc_repo):
    '''Add stores markdown as text, leaves passages and embeddings alone, and export ignores the note.'''

    document = DocumentAggregate(id='doc-001', title='Notes', status='draft')
    doc_repo.save(document)
    section = DomainEvent.handle(
        AddDocumentSection,
        dependencies={'document_service': doc_repo},
        document_id='doc-001',
        title='Intro',
        content='Hello **world**',
        content_type='markdown',
        position=0,
    )
    before = doc_repo.get('doc-001')
    exported_before = DomainEvent.handle(
        ExportDocumentMarkdown,
        dependencies={'document_service': doc_repo},
        id='doc-001',
    )

    comment = DomainEvent.handle(
        AddSectionComment,
        dependencies={'document_service': doc_repo},
        document_id='doc-001',
        section_id=section.id,
        author='ada',
        text='# not a heading\n**bold**',
        id='cmt-001',
    )
    after = doc_repo.get('doc-001')
    exported_after = DomainEvent.handle(
        ExportDocumentMarkdown,
        dependencies={'document_service': doc_repo},
        id='doc-001',
    )

    assert comment.text == '# not a heading\n**bold**'
    assert before.sections[0].paragraphs == after.sections[0].paragraphs
    assert 'comments' not in type(after.sections[0]).model_fields
    assert doc_repo.get_embedding(section.id) is None
    assert exported_before == exported_after
    assert '**bold**' not in exported_after
    assert doc_repo.list_comments(section.id)[0].text == comment.text

# ** test: import_does_not_write_comments
def test_import_does_not_write_comments(doc_repo):
    '''Import rebuilds passages and does not write a comment row.'''

    document = DomainEvent.handle(
        ImportMarkdownDocument,
        dependencies={'document_service': doc_repo},
        content='# Imported\n\nBody text\n',
    )
    assert doc_repo.list_comments(document.sections[0].id) == []
    with H5Client(path=doc_repo.h5_file, mode='r') as h5:
        assert not h5.node_exists('/kb/documents/section_comments')

# ** test: max_length_is_stored_not_truncated
def test_max_length_is_stored_not_truncated(doc_repo):
    '''A value at the cap is stored whole. One character over is not written.'''

    doc_repo.save(DocumentAggregate(id='doc-001', title='Notes', status='draft'))
    section = DocumentSectionAggregate(
        id='sec-001', document_id='doc-001', title='Intro', position=0,
        created_at='2026-01-01T00:00:00+00:00', updated_at='2026-01-01T00:00:00+00:00',
    )
    doc_repo.save_section(section)
    author = 'a' * 512
    text = 't' * 8192

    stored = DomainEvent.handle(
        AddSectionComment,
        dependencies={'document_service': doc_repo},
        document_id='doc-001',
        section_id='sec-001',
        author=author,
        text=text,
        id='cmt-max',
    )
    assert stored.author == author
    assert stored.text == text
    assert doc_repo.list_comments('sec-001')[0].text == text

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddSectionComment,
            dependencies={'document_service': doc_repo},
            document_id='doc-001',
            section_id='sec-001',
            author='ada',
            text='t' * 8193,
            id='cmt-over',
        )
    assert [item.id for item in doc_repo.list_comments('sec-001')] == ['cmt-max']
