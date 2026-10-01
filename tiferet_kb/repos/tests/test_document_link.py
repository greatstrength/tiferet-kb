"""tiferet_kb Document Link Repository Tests"""

# *** imports

# ** core
import inspect

# ** infra
import pytest
from tiferet.assets import TiferetError
from tiferet.events import DomainEvent
from tiferet_h5.utils import H5Client

# ** app
from ...assets.errors import (
    KB_DOCUMENT_LINK_ALREADY_EXISTS_ID,
    KB_DOCUMENT_NOT_FOUND_ID,
    KB_INVALID_DOCUMENT_LINK_ID,
)
from ...domain.document_link import (
    DOCUMENT_LINK_REFERENCES,
    DOCUMENT_LINK_RELATED_TO,
    DOCUMENT_LINK_SUPERSEDES,
)
from ...domain.segment import Paragraph, TextSegment
from ...events.document import GetDocument, ListDocuments, RemoveDocument
from ...events.document_link import (
    AddDocumentLink,
    ListDocumentLinks,
    RemoveDocumentLink,
)
from ...mappers.document import DocumentAggregate, DocumentSectionAggregate
from ...mappers.document_link import DocumentLinkAggregate, DocumentLinkTableObject
from ..document import (
    DOCUMENTS_GROUP,
    DOCUMENTS_TABLE,
    DOCUMENT_LINKS_TABLE,
    DocumentH5Repository,
)
from ..tag import TagH5Repository

# *** fixtures

# ** fixture: h5_file
@pytest.fixture
def h5_file(tmp_path) -> str:
    '''Provide a temporary HDF5 file path.'''

    return str(tmp_path / 'links.h5')

# ** fixture: doc_repo
@pytest.fixture
def doc_repo(h5_file: str) -> DocumentH5Repository:
    '''Provide a document repository backed by a temporary file.'''

    return DocumentH5Repository(h5_file=h5_file)

# *** functions

# ** function: save_doc
def save_doc(doc_repo, doc_id: str, status: str = 'draft') -> DocumentAggregate:
    '''Save a document header with a fixed timestamp.'''

    document = DocumentAggregate(
        id=doc_id,
        title=f'Title {doc_id}',
        status=status,
        category_id='cat-1',
        template_id='tpl-1',
        folder_id='fld-1',
        created_at='2026-01-01T00:00:00+00:00',
        updated_at='2026-01-01T00:00:00+00:00',
    )
    doc_repo.save(document)
    return document

# ** function: add
def add(doc_repo, source_id: str, target_id: str, link_type: str, link_id: str | None = None):
    '''Add a link through the event.'''

    return DomainEvent.handle(
        AddDocumentLink,
        dependencies={'document_service': doc_repo},
        source_id=source_id,
        target_id=target_id,
        link_type=link_type,
        id=link_id,
    )

# ** function: listed
def listed(doc_repo, document_id: str, direction: str | None = None, link_type: str | None = None):
    '''List links through the event.'''

    kwargs = {'document_id': document_id}
    if direction is not None:
        kwargs['direction'] = direction
    if link_type is not None:
        kwargs['link_type'] = link_type
    return DomainEvent.handle(
        ListDocumentLinks,
        dependencies={'document_service': doc_repo},
        **kwargs,
    )

# ** function: remove_doc
def remove_doc(doc_repo, doc_id: str) -> str:
    '''Remove a document through the event, including tag cleanup.'''

    return DomainEvent.handle(
        RemoveDocument,
        dependencies={
            'document_service': doc_repo,
            'tag_service': TagH5Repository(h5_file=doc_repo.h5_file),
        },
        id=doc_id,
    )

# *** tests

# ** test_int: add_stores_one_row
def test_int_add_stores_one_row(doc_repo, h5_file):
    '''Add between two documents stores one row and returns the five fields.'''

    save_doc(doc_repo, 'doc-001', status='draft')
    save_doc(doc_repo, 'doc-002', status='archived')
    before = doc_repo.list()

    link = add(doc_repo, 'doc-001', 'doc-002', DOCUMENT_LINK_REFERENCES, link_id='link-001')

    assert link.id == 'link-001'
    assert link.source_id == 'doc-001'
    assert link.target_id == 'doc-002'
    assert link.link_type == 'references'
    assert link.created_at
    assert len(doc_repo.list()) == len(before)
    with H5Client(path=h5_file, mode='r') as h5:
        rows = h5.read_rows(DOCUMENT_LINKS_TABLE)
        assert len(rows) == 1
        assert rows[0]['source_id'] == 'doc-001'
        assert h5.get_node_attr(DOCUMENT_LINKS_TABLE, 'schema_version') == DocumentLinkTableObject.schema_fingerprint()

# ** test_int: documented_and_open_types_are_stored_unchanged
def test_int_documented_types_are_stored_unchanged(doc_repo, h5_file):
    '''The documented names are stored as given. Any other string is rejected.'''

    save_doc(doc_repo, 'doc-001')
    save_doc(doc_repo, 'doc-002')
    save_doc(doc_repo, 'doc-003', status='published')

    supersedes = add(doc_repo, 'doc-001', 'doc-002', DOCUMENT_LINK_SUPERSEDES)
    related = add(doc_repo, 'doc-001', 'doc-003', DOCUMENT_LINK_RELATED_TO)
    assert supersedes.link_type == 'supersedes'
    assert related.link_type == 'related_to'

    with pytest.raises(TiferetError) as exc_info:
        add(doc_repo, 'doc-002', 'doc-003', 'cites')
    assert exc_info.value.error_code == KB_INVALID_DOCUMENT_LINK_ID
    with H5Client(path=h5_file, mode='r') as h5:
        assert {row['link_type'] for row in h5.read_rows(DOCUMENT_LINKS_TABLE)} == {
            'supersedes',
            'related_to',
        }

# ** test_int: add_missing_endpoint_stores_nothing
def test_int_add_missing_endpoint_stores_nothing(doc_repo, h5_file):
    '''A missing source or target stores nothing and does not create the link table.'''

    save_doc(doc_repo, 'doc-001')

    with pytest.raises(TiferetError) as missing_target:
        add(doc_repo, 'doc-001', 'missing', 'references')
    assert missing_target.value.error_code == KB_DOCUMENT_NOT_FOUND_ID

    with pytest.raises(TiferetError) as missing_source:
        add(doc_repo, 'missing', 'doc-001', 'references')
    assert missing_source.value.error_code == KB_DOCUMENT_NOT_FOUND_ID

    with H5Client(path=h5_file, mode='r') as h5:
        assert not h5.node_exists(DOCUMENT_LINKS_TABLE)

# ** test_int: self_link_is_rejected
def test_int_self_link_is_rejected(doc_repo, h5_file):
    '''A link whose ends are the same document is not stored.'''

    save_doc(doc_repo, 'doc-001')
    with pytest.raises(TiferetError) as exc_info:
        add(doc_repo, 'doc-001', 'doc-001', 'related_to')
    assert exc_info.value.error_code == KB_INVALID_DOCUMENT_LINK_ID
    with H5Client(path=h5_file, mode='r') as h5:
        assert not h5.node_exists(DOCUMENT_LINKS_TABLE)

# ** test_int: overlong_values_are_not_clipped
def test_int_overlong_values_are_not_clipped(doc_repo, h5_file):
    '''A type or id that does not fit is rejected and not clipped into a row.'''

    save_doc(doc_repo, 'doc-001')
    save_doc(doc_repo, 'doc-002')
    stored = add(doc_repo, 'doc-001', 'doc-002', DOCUMENT_LINK_REFERENCES)
    assert stored.link_type == DOCUMENT_LINK_REFERENCES

    with pytest.raises(TiferetError) as type_error:
        add(doc_repo, 'doc-002', 'doc-001', 'z' * (DocumentLinkTableObject.type_width() + 1))
    assert type_error.value.error_code == KB_INVALID_DOCUMENT_LINK_ID

    with pytest.raises(TiferetError) as id_error:
        add(
            doc_repo,
            'doc-002',
            'doc-001',
            DOCUMENT_LINK_SUPERSEDES,
            link_id='i' * (DocumentLinkTableObject.identifier_width() + 1),
        )
    assert id_error.value.error_code == KB_INVALID_DOCUMENT_LINK_ID

    with H5Client(path=h5_file, mode='r') as h5:
        rows = h5.read_rows(DOCUMENT_LINKS_TABLE)
        assert len(rows) == 1
        assert rows[0]['link_type'] == DOCUMENT_LINK_REFERENCES

# ** test_int: duplicate_triple_and_id_are_refused
def test_int_duplicate_triple_and_id_are_refused(doc_repo):
    '''A repeated triple or a repeated id stores nothing and leaves the first row.'''

    save_doc(doc_repo, 'doc-001')
    save_doc(doc_repo, 'doc-002')
    save_doc(doc_repo, 'doc-003')
    first = add(doc_repo, 'doc-001', 'doc-002', 'references', link_id='link-001')

    with pytest.raises(TiferetError) as triple_error:
        add(doc_repo, 'doc-001', 'doc-002', '  references  ')
    assert triple_error.value.error_code == KB_DOCUMENT_LINK_ALREADY_EXISTS_ID

    with pytest.raises(TiferetError) as id_error:
        add(doc_repo, 'doc-001', 'doc-003', 'related_to', link_id='link-001')
    assert id_error.value.error_code == KB_DOCUMENT_LINK_ALREADY_EXISTS_ID

    rows = listed(doc_repo, 'doc-001', direction='outgoing')
    assert [row.id for row in rows] == [first.id]

# ** test_int: different_type_and_reverse_are_distinct
def test_int_different_type_and_reverse_are_distinct(doc_repo):
    '''A different type, and the reversed pair, are separate adds.'''

    save_doc(doc_repo, 'doc-001')
    save_doc(doc_repo, 'doc-002')
    first = add(doc_repo, 'doc-001', 'doc-002', 'references')
    second = add(doc_repo, 'doc-001', 'doc-002', 'supersedes')
    reverse = add(doc_repo, 'doc-002', 'doc-001', 'references')

    outgoing = listed(doc_repo, 'doc-001', direction='outgoing')
    assert {row.id for row in outgoing} == {first.id, second.id}
    assert reverse.id not in {row.id for row in outgoing}
    assert listed(doc_repo, 'doc-001', direction='incoming')[0].id == reverse.id

# ** test_int: list_direction_order_and_filter
def test_int_list_direction_order_and_filter(doc_repo):
    '''List partitions by direction and orders each direction by time, then id.'''

    save_doc(doc_repo, 'doc-001')
    save_doc(doc_repo, 'doc-002')
    save_doc(doc_repo, 'doc-003')

    # Explicit timestamps lock the order independent of the clock.
    doc_repo.add_link(DocumentLinkAggregate(
        id='b-link', source_id='doc-001', target_id='doc-002',
        link_type='references', created_at='2026-02-01T00:00:00+00:00',
    ))
    doc_repo.add_link(DocumentLinkAggregate(
        id='a-link', source_id='doc-001', target_id='doc-003',
        link_type='supersedes', created_at='2026-01-01T00:00:00+00:00',
    ))
    doc_repo.add_link(DocumentLinkAggregate(
        id='c-link', source_id='doc-001', target_id='doc-002',
        link_type='related_to', created_at='2026-01-01T00:00:00+00:00',
    ))
    doc_repo.add_link(DocumentLinkAggregate(
        id='in-link', source_id='doc-002', target_id='doc-001',
        link_type='references', created_at='2020-01-01T00:00:00+00:00',
    ))

    outgoing = listed(doc_repo, 'doc-001', direction='outgoing')
    incoming = listed(doc_repo, 'doc-001', direction='incoming')
    both = listed(doc_repo, 'doc-001')
    typed = listed(doc_repo, 'doc-001', direction='outgoing', link_type='references')

    assert [row.id for row in outgoing] == ['a-link', 'c-link', 'b-link']
    assert [row.id for row in incoming] == ['in-link']
    assert [row.id for row in both] == ['a-link', 'c-link', 'b-link', 'in-link']
    assert len({row.id for row in both}) == len(both)
    assert [row.id for row in typed] == ['b-link']

# ** test_int: list_missing_table_is_empty
def test_int_list_missing_table_is_empty(doc_repo, h5_file):
    '''An existing document with no link table lists empty and does not create the table.'''

    save_doc(doc_repo, 'doc-001')
    assert listed(doc_repo, 'doc-001') == []
    with H5Client(path=h5_file, mode='r') as h5:
        assert not h5.node_exists(DOCUMENT_LINKS_TABLE)

    with pytest.raises(TiferetError) as exc_info:
        listed(doc_repo, 'missing')
    assert exc_info.value.error_code == KB_DOCUMENT_NOT_FOUND_ID

# ** test_int: remove_is_idempotent_and_keeps_the_table
def test_int_remove_is_idempotent_and_keeps_the_table(doc_repo, h5_file):
    '''Remove deletes the row, a second remove succeeds, and the table node stays.'''

    save_doc(doc_repo, 'doc-001')
    save_doc(doc_repo, 'doc-002')
    link = add(doc_repo, 'doc-001', 'doc-002', 'references', link_id='link-001')

    calls = []
    original = doc_repo.node_repo.remove_node

    def spy(h5, path, recursive=False):
        calls.append(path)
        return original(h5, path, recursive=recursive)

    doc_repo.node_repo.remove_node = spy
    removed = DomainEvent.handle(
        RemoveDocumentLink,
        dependencies={'document_service': doc_repo},
        id=link.id,
    )
    again = DomainEvent.handle(
        RemoveDocumentLink,
        dependencies={'document_service': doc_repo},
        id=link.id,
    )
    assert removed == 'link-001'
    assert again == 'link-001'
    assert DOCUMENT_LINKS_TABLE not in calls
    assert listed(doc_repo, 'doc-001') == []
    with H5Client(path=h5_file, mode='r') as h5:
        assert h5.node_exists(DOCUMENT_LINKS_TABLE)
        assert h5.read_rows(DOCUMENT_LINKS_TABLE) == []

# ** test_int: delete_document_cascades_links
def test_int_delete_document_cascades_links(doc_repo, h5_file):
    '''Deleting a source, a target, or both drops only that document's link rows.'''

    save_doc(doc_repo, 'doc-001')
    save_doc(doc_repo, 'doc-002')
    save_doc(doc_repo, 'doc-003')
    add(doc_repo, 'doc-001', 'doc-002', 'references', link_id='gone')
    add(doc_repo, 'doc-002', 'doc-001', 'supersedes', link_id='also-gone')
    kept = add(doc_repo, 'doc-002', 'doc-003', 'related_to', link_id='kept')

    calls = []
    original = doc_repo.node_repo.remove_node

    def spy(h5, path, recursive=False):
        calls.append(path)
        return original(h5, path, recursive=recursive)

    doc_repo.node_repo.remove_node = spy
    remove_doc(doc_repo, 'doc-001')
    assert DOCUMENT_LINKS_TABLE not in calls
    remaining = doc_repo.list_links('doc-002')
    assert [row.id for row in remaining] == [kept.id]
    with H5Client(path=h5_file, mode='r') as h5:
        assert h5.node_exists(DOCUMENT_LINKS_TABLE)
        assert {row['id'] for row in h5.read_rows(DOCUMENT_LINKS_TABLE)} == {'kept'}

# ** test_int: delete_absent_document_still_clears_links
def test_int_delete_absent_document_still_clears_links(doc_repo, h5_file):
    '''A missing header still drops leftover link rows. A missing table does not fail delete.'''

    save_doc(doc_repo, 'doc-001')
    save_doc(doc_repo, 'doc-002')
    add(doc_repo, 'doc-001', 'doc-002', 'references', link_id='orphan')

    with H5Client(path=h5_file, mode='a') as h5:
        h5.remove_rows(DOCUMENTS_TABLE, '(id == b"doc-001")')

    remove_doc(doc_repo, 'doc-001')
    assert doc_repo.list_links('doc-002') == []

    save_doc(doc_repo, 'doc-004')
    remove_doc(doc_repo, 'doc-004')
    remove_doc(doc_repo, 'already-gone')

# ** test_int: link_commands_do_not_touch_documents_or_passages
def test_int_link_commands_do_not_touch_documents_or_passages(doc_repo):
    '''Add, list, remove, and cascade leave headers, sections, and text links alone.'''

    save_doc(doc_repo, 'doc-001', status='published')
    save_doc(doc_repo, 'doc-002', status='archived')
    section = DocumentSectionAggregate(
        id='sec-001',
        document_id='doc-001',
        title='See also',
        content_type='markdown',
        position=0,
        created_at='2026-01-01T00:00:00+00:00',
        updated_at='2026-01-01T00:00:00+00:00',
        paragraphs=[Paragraph(
            id='para-001',
            section_id='sec-001',
            position=0,
            segments=[TextSegment(
                id='seg-001',
                position=0,
                text='elsewhere',
                format_type='link',
                link_url='https://example.test/page',
            )],
        )],
    )
    doc_repo.save_section(section)

    def snapshot(doc_id: str):
        document = doc_repo.get(doc_id)
        return (
            document.updated_at,
            document.status,
            document.category_id,
            document.template_id,
            document.folder_id,
            [
                (
                    item.id,
                    item.title,
                    [(seg.format_type, seg.text, seg.link_url) for para in item.paragraphs for seg in para.segments],
                )
                for item in document.sections
            ],
        )

    before = {doc_id: snapshot(doc_id) for doc_id in ('doc-001', 'doc-002')}
    link = add(doc_repo, 'doc-001', 'doc-002', 'references')
    listed(doc_repo, 'doc-001')
    assert snapshot('doc-001') == before['doc-001']
    assert snapshot('doc-002') == before['doc-002']

    DomainEvent.handle(
        RemoveDocumentLink,
        dependencies={'document_service': doc_repo},
        id=link.id,
    )
    assert snapshot('doc-001') == before['doc-001']

    add(doc_repo, 'doc-001', 'doc-002', 'supersedes')
    remove_doc(doc_repo, 'doc-002')
    after = doc_repo.get('doc-001')
    segment = after.sections[0].paragraphs[0].segments[0]
    assert segment.format_type == 'link'
    assert segment.link_url == 'https://example.test/page'
    assert segment.text == 'elsewhere'
    assert 'links' not in type(after).model_fields
    assert 'content' not in type(after).model_fields
    assert 'content' not in type(after.sections[0]).model_fields

# ** test_int: get_and_list_keep_their_parameters
def test_int_get_and_list_keep_their_parameters():
    '''Get and list do not gain a links parameter. The existing filters stay.'''

    get_params = inspect.signature(GetDocument.execute).parameters
    list_params = inspect.signature(ListDocuments.execute).parameters
    repo_params = inspect.signature(DocumentH5Repository.list).parameters
    assert 'id' in get_params
    assert 'links' not in get_params
    assert 'folder_id' in list_params
    assert 'category_id' in list_params
    assert 'status' in list_params
    assert 'title' in list_params
    assert 'property_name' in list_params
    assert 'tag_id' in list_params
    assert 'visibility' in list_params
    assert 'owner_id' in list_params
    assert 'links' not in list_params
    assert 'folder_id' in repo_params
    assert 'category_id' in repo_params
    assert 'status' in repo_params
    assert 'title' in repo_params
    assert 'include_sections' in repo_params
    assert 'include_properties' in repo_params
    assert 'property_name' in repo_params
    assert 'visibility' in repo_params
    assert 'owner_id' in repo_params

# ** test_int: link_table_is_sibling_of_header
def test_int_link_table_is_sibling_of_header():
    '''The link table sits in the documents group, beside the header table.'''

    assert DOCUMENT_LINKS_TABLE == f'{DOCUMENTS_GROUP}/document_links'
    assert DOCUMENT_LINKS_TABLE.rsplit('/', 1)[0] == DOCUMENTS_TABLE.rsplit('/', 1)[0]
