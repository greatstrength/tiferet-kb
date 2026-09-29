"""tiferet_kb Document Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events import DomainEvent
from tiferet.assets import TiferetError

from ...interfaces.document import DocumentService
from ...interfaces.tag import TagService
from ...assets.errors import (
    KB_DOCUMENT_SECTION_NOT_FOUND_ID,
    KB_SECTION_REVISION_NOT_FOUND_ID,
)
from ...domain.document import SectionRevision
from ...domain.segment import Paragraph, TextSegment
from ...mappers.document import DocumentAggregate, DocumentSectionAggregate
from ..document import (
    AddDocument,
    GetDocument,
    ListDocuments,
    UpdateDocument,
    SetDocumentVisibility,
    RemoveDocument,
    AddDocumentSection,
    UpdateDocumentSection,
    ListDocumentSectionRevisions,
    RestoreDocumentSectionRevision,
    RemoveDocumentSection,
    ReorderDocumentSections,
)

# *** fixtures

# ** fixture: mock_document_service
@pytest.fixture
def mock_document_service() -> DocumentService:
    '''Mock DocumentService for testing.'''
    return mock.Mock(spec=DocumentService)

# ** fixture: mock_tag_service
@pytest.fixture
def mock_tag_service() -> TagService:
    '''Mock TagService for testing.'''
    return mock.Mock(spec=TagService)
# ** fixture: sample_document
@pytest.fixture
def sample_document() -> DocumentAggregate:
    '''Sample DocumentAggregate instance for testing.'''
    return DocumentAggregate(
        id='doc-001',
        title='Test Document',
        status='draft',
        created_at='2026-01-01T00:00:00+00:00',
        updated_at='2026-01-01T00:00:00+00:00',
    )

# ** fixture: sample_section
@pytest.fixture
def sample_section() -> DocumentSectionAggregate:
    '''Sample DocumentSectionAggregate instance for testing.'''
    return DocumentSectionAggregate(
        id='sec-001',
        document_id='doc-001',
        title='Introduction',
        content_type='markdown',
        heading_level=2,
        position=0,
        created_at='2026-01-01T00:00:00+00:00',
        updated_at='2026-01-01T00:00:00+00:00',
    )

# *** tests

# ** test: add_document_success
def test_add_document_success(mock_document_service):
    '''Test successful creation of a new document.'''

    mock_document_service.exists.return_value = False

    result = DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': mock_document_service},
        title='My New Document',
    )

    assert result.title == 'My New Document'
    assert result.status == 'draft'
    assert result.id is not None
    mock_document_service.save.assert_called_once()

# ** test: add_document_with_explicit_id
def test_add_document_with_explicit_id(mock_document_service):
    '''Test creation with an explicit ID.'''

    mock_document_service.exists.return_value = False

    result = DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': mock_document_service},
        title='Test',
        id='custom-id',
    )

    assert result.id == 'custom-id'

# ** test: add_document_duplicate
def test_add_document_duplicate(mock_document_service):
    '''Test that adding a duplicate document raises an error.'''

    mock_document_service.exists.return_value = True

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddDocument,
            dependencies={'document_service': mock_document_service},
            title='Test',
            id='existing-id',
        )

# ** test: add_document_missing_title
def test_add_document_missing_title(mock_document_service):
    '''Test that AddDocument raises when title is missing.'''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddDocument,
            dependencies={'document_service': mock_document_service},
        )

# ** test: get_document_success
def test_get_document_success(mock_document_service, sample_document):
    '''Test successful retrieval of a document.'''

    mock_document_service.get.return_value = sample_document

    result = DomainEvent.handle(
        GetDocument,
        dependencies={'document_service': mock_document_service},
        id='doc-001',
    )

    assert result is sample_document

# ** test: get_document_not_found
def test_get_document_not_found(mock_document_service):
    '''Test that getting a non-existent document raises.'''

    mock_document_service.get.return_value = None

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            GetDocument,
            dependencies={'document_service': mock_document_service},
            id='nonexistent',
        )

# ** test: list_documents_success
def test_list_documents_success(mock_document_service, mock_tag_service, sample_document):
    '''Test listing documents.'''

    mock_document_service.list.return_value = [sample_document]

    result = DomainEvent.handle(
        ListDocuments,
        dependencies={
            'document_service': mock_document_service,
            'tag_service': mock_tag_service,
        },
    )

    assert len(result) == 1
    mock_tag_service.list_document_ids.assert_not_called()

# ** test: list_documents_with_filters
def test_list_documents_with_filters(mock_document_service, mock_tag_service):
    '''Test listing documents with filters.'''

    mock_document_service.list.return_value = []

    DomainEvent.handle(
        ListDocuments,
        dependencies={
            'document_service': mock_document_service,
            'tag_service': mock_tag_service,
        },
        folder_id='folder-1',
        status='draft',
    )

    mock_document_service.list.assert_called_once_with(
        folder_id='folder-1',
        category_id=None,
        status='draft',
        title=None,
        include_properties=False,
        property_name=None,
        property_value=None,
        property_value_type=None,
        visibility=None,
        owner_id=None,
    )
    mock_tag_service.list_document_ids.assert_not_called()

# ** test: list_documents_forwards_title
def test_list_documents_forwards_title(mock_document_service, mock_tag_service):
    '''ListDocuments forwards an exact title, including when it is set.'''

    mock_document_service.list.return_value = []

    DomainEvent.handle(
        ListDocuments,
        dependencies={
            'document_service': mock_document_service,
            'tag_service': mock_tag_service,
        },
        title='memory:agent:default',
    )

    mock_document_service.list.assert_called_once_with(
        folder_id=None,
        category_id=None,
        status=None,
        title='memory:agent:default',
        include_properties=False,
        property_name=None,
        property_value=None,
        property_value_type=None,
        visibility=None,
        owner_id=None,
    )
    mock_tag_service.list_document_ids.assert_not_called()

# ** test: update_document_success
def test_update_document_success(mock_document_service, sample_document):
    '''Test successful update of a document attribute.'''

    mock_document_service.get.return_value = sample_document

    result = DomainEvent.handle(
        UpdateDocument,
        dependencies={'document_service': mock_document_service},
        id='doc-001',
        attribute='title',
        value='Updated Title',
    )

    assert result.title == 'Updated Title'
    mock_document_service.save.assert_called_once()

# ** test: update_document_invalid_attribute
def test_update_document_invalid_attribute(mock_document_service):
    '''Test that updating an invalid attribute raises.'''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            UpdateDocument,
            dependencies={'document_service': mock_document_service},
            id='doc-001',
            attribute='nonexistent',
            value='bad',
        )

# ** test: update_document_invalid_status
def test_update_document_invalid_status(mock_document_service):
    '''Test that an invalid status value raises.'''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            UpdateDocument,
            dependencies={'document_service': mock_document_service},
            id='doc-001',
            attribute='status',
            value='invalid_status',
        )

# ** test: remove_document_success
def test_remove_document_success(mock_document_service, mock_tag_service):
    '''Test successful removal of a document.'''

    result = DomainEvent.handle(
        RemoveDocument,
        dependencies={
            'document_service': mock_document_service,
            'tag_service': mock_tag_service,
        },
        id='doc-001',
    )

    assert result == 'doc-001'
    mock_tag_service.clear_document.assert_called_once_with('doc-001')
    mock_document_service.delete.assert_called_once_with('doc-001')

# *** section event tests

# ** test: add_document_section_success
def test_add_document_section_success(mock_document_service):
    '''Test successful addition of a section.'''

    mock_document_service.exists.return_value = True
    mock_document_service.get_sections.return_value = []

    result = DomainEvent.handle(
        AddDocumentSection,
        dependencies={'document_service': mock_document_service},
        document_id='doc-001',
        title='Introduction',
        content='Hello **world**',
    )

    assert result.title == 'Introduction'
    assert result.content_type == 'markdown'
    assert result.document_id == 'doc-001'
    assert result.position == 0
    # Verify paragraphs were parsed from markdown content.
    assert len(result.paragraphs) == 1
    assert result.paragraphs[0].segments[1].format_type == 'bold'
    mock_document_service.save_section.assert_called_once()
    mock_document_service.append_section_revision.assert_not_called()

# ** test: add_document_section_with_position
def test_add_document_section_with_position(mock_document_service):
    '''Test adding a section with an explicit position.'''

    mock_document_service.exists.return_value = True

    result = DomainEvent.handle(
        AddDocumentSection,
        dependencies={'document_service': mock_document_service},
        document_id='doc-001',
        title='Middle Section',
        position=1,
    )

    assert result.position == 1

# ** test: add_document_section_invalid_content_type
def test_add_document_section_invalid_content_type(mock_document_service):
    '''Test that an invalid content type raises.'''

    mock_document_service.exists.return_value = True

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddDocumentSection,
            dependencies={'document_service': mock_document_service},
            document_id='doc-001',
            title='Bad',
            content_type='invalid',
        )

# ** test: add_document_section_document_not_found
def test_add_document_section_document_not_found(mock_document_service):
    '''Test that adding a section to a non-existent document raises.'''

    mock_document_service.exists.return_value = False

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddDocumentSection,
            dependencies={'document_service': mock_document_service},
            document_id='nonexistent',
            title='Intro',
            content_type='text',
        )

# ** test: add_document_section_missing_params
def test_add_document_section_missing_title(mock_document_service):
    '''Test that missing title raises.'''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddDocumentSection,
            dependencies={'document_service': mock_document_service},
            document_id='doc-001',
        )

# ** test: update_document_section_success
def test_update_document_section_success(mock_document_service, sample_section):
    '''Test successful update of a section via content re-parse.'''

    mock_document_service.get_sections.return_value = [sample_section]

    result = DomainEvent.handle(
        UpdateDocumentSection,
        dependencies={'document_service': mock_document_service},
        id='sec-001',
        attribute='content',
        value='Updated **content**',
        document_id='doc-001',
    )

    # Content was re-parsed into paragraphs with formatting.
    assert len(result.paragraphs) == 1
    assert result.paragraphs[0].segments[1].format_type == 'bold'
    assert 'content' not in type(result).model_fields
    mock_document_service.append_section_revision.assert_called_once()
    mock_document_service.save_section.assert_called_once()
    names = [call[0] for call in mock_document_service.mock_calls]
    assert names.index('append_section_revision') < names.index('save_section')

# ** test: update_document_section_rename
def test_update_document_section_rename(mock_document_service, sample_section):
    '''Test renaming a section.'''

    mock_document_service.get_sections.return_value = [sample_section]

    result = DomainEvent.handle(
        UpdateDocumentSection,
        dependencies={'document_service': mock_document_service},
        id='sec-001',
        attribute='title',
        value='Updated Title',
        document_id='doc-001',
    )

    assert result.title == 'Updated Title'
    mock_document_service.append_section_revision.assert_not_called()

# ** test: update_document_section_invalid_attribute
def test_update_document_section_invalid_attribute(mock_document_service):
    '''Test that an invalid section attribute raises.'''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            UpdateDocumentSection,
            dependencies={'document_service': mock_document_service},
            id='sec-001',
            attribute='nonexistent',
            value='bad',
            document_id='doc-001',
        )

# ** test: update_document_section_not_found
def test_update_document_section_not_found(mock_document_service):
    '''Test that updating a non-existent section raises.'''

    mock_document_service.get_sections.return_value = []

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            UpdateDocumentSection,
            dependencies={'document_service': mock_document_service},
            id='nonexistent',
            attribute='content',
            value='test',
            document_id='doc-001',
        )

# ** test: update_document_section_invalid_content_type
def test_update_document_section_invalid_content_type(mock_document_service):
    '''Test that an invalid content_type value raises.'''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            UpdateDocumentSection,
            dependencies={'document_service': mock_document_service},
            id='sec-001',
            attribute='content_type',
            value='invalid',
            document_id='doc-001',
        )

# ** test: remove_document_section_success
def test_remove_document_section_success(mock_document_service):
    '''Test successful removal of a section.'''

    result = DomainEvent.handle(
        RemoveDocumentSection,
        dependencies={'document_service': mock_document_service},
        id='sec-001',
    )

    assert result == 'sec-001'
    mock_document_service.delete_section.assert_called_once_with('sec-001')

# ** test: reorder_document_sections_success
def test_reorder_document_sections_success(mock_document_service):
    '''Test successful reordering of sections.'''

    mock_document_service.exists.return_value = True

    result = DomainEvent.handle(
        ReorderDocumentSections,
        dependencies={'document_service': mock_document_service},
        document_id='doc-001',
        section_ids=['sec-002', 'sec-001'],
    )

    assert result == 'doc-001'
    mock_document_service.reorder_sections.assert_called_once_with('doc-001', ['sec-002', 'sec-001'])
    mock_document_service.append_section_revision.assert_not_called()

# ** test: reorder_document_sections_document_not_found
def test_reorder_document_sections_document_not_found(mock_document_service):
    '''Test that reordering for a non-existent document raises.'''

    mock_document_service.exists.return_value = False

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            ReorderDocumentSections,
            dependencies={'document_service': mock_document_service},
            document_id='nonexistent',
            section_ids=['sec-001'],
        )

# *** tests: RFP-008 visibility

# ** test: set_document_visibility_success
def test_set_document_visibility_success(mock_document_service, sample_document):
    '''SetDocumentVisibility updates access fields and leaves the rest of the header alone.'''

    sample_document.sections = []
    mock_document_service.get.return_value = sample_document
    before = sample_document.updated_at

    result = DomainEvent.handle(
        SetDocumentVisibility,
        dependencies={'document_service': mock_document_service},
        id='doc-001',
        visibility='private',
        owner_id='owner-1',
    )

    assert result.visibility == 'private'
    assert result.owner_id == 'owner-1'
    assert result.title == 'Test Document'
    assert result.status == 'draft'
    assert result.updated_at != before
    mock_document_service.save.assert_called_once()
    mock_document_service.exists.assert_not_called()

# ** test: set_document_visibility_clears_owner
def test_set_document_visibility_clears_owner(mock_document_service, sample_document):
    '''An omitted, empty, or whitespace owner clears the stored owner.'''

    sample_document.owner_id = 'owner-1'
    mock_document_service.get.return_value = sample_document

    result = DomainEvent.handle(
        SetDocumentVisibility,
        dependencies={'document_service': mock_document_service},
        id='doc-001',
        visibility='public',
        owner_id='   ',
    )

    assert result.visibility == 'public'
    assert result.owner_id is None

# ** test: set_document_visibility_not_found
def test_set_document_visibility_not_found(mock_document_service):
    '''A missing document raises the existing not-found error and is not created.'''

    mock_document_service.get.return_value = None

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            SetDocumentVisibility,
            dependencies={'document_service': mock_document_service},
            id='missing',
            visibility='private',
        )

    assert exc_info.value.error_code == 'KB_DOCUMENT_NOT_FOUND'
    mock_document_service.save.assert_not_called()

# ** test: set_document_visibility_rejects_status_token
def test_set_document_visibility_rejects_status_token(mock_document_service):
    '''A status token is KB_INVALID_VISIBILITY, not KB_INVALID_DOCUMENT_STATUS.'''

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            SetDocumentVisibility,
            dependencies={'document_service': mock_document_service},
            id='doc-001',
            visibility='published',
        )

    assert exc_info.value.error_code == 'KB_INVALID_VISIBILITY'
    assert 'status' not in str(exc_info.value)
    mock_document_service.get.assert_not_called()

# ** test: add_document_visibility
def test_add_document_visibility(mock_document_service):
    '''AddDocument accepts visibility and owner, and rejects a token outside the set.'''

    mock_document_service.exists.return_value = False

    created = DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': mock_document_service},
        title='Owned',
        visibility='restricted',
        owner_id='owner-2',
    )
    assert created.visibility == 'restricted'
    assert created.owner_id == 'owner-2'

    omitted = DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': mock_document_service},
        title='Plain',
    )
    assert omitted.visibility == 'public'
    assert omitted.owner_id is None

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            AddDocument,
            dependencies={'document_service': mock_document_service},
            title='Bad',
            visibility='Draft',
        )
    assert exc_info.value.error_code == 'KB_INVALID_VISIBILITY'

# ** test: list_documents_passes_access_filters
def test_list_documents_passes_access_filters(mock_document_service, mock_tag_service):
    '''ListDocuments passes visibility and owner and still omits include_sections.'''

    mock_document_service.list.return_value = []

    DomainEvent.handle(
        ListDocuments,
        dependencies={
            'document_service': mock_document_service,
            'tag_service': mock_tag_service,
        },
        visibility='public',
        owner_id='owner-1',
    )

    mock_document_service.list.assert_called_once_with(
        folder_id=None,
        category_id=None,
        status=None,
        title=None,
        include_properties=False,
        property_name=None,
        property_value=None,
        property_value_type=None,
        visibility='public',
        owner_id='owner-1',
    )

# ** test: list_documents_rejects_unknown_visibility
def test_list_documents_rejects_unknown_visibility(mock_document_service, mock_tag_service):
    '''An unrecognized list filter is KB_INVALID_VISIBILITY.'''

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            ListDocuments,
            dependencies={
                'document_service': mock_document_service,
                'tag_service': mock_tag_service,
            },
            visibility='archived',
        )
    assert exc_info.value.error_code == 'KB_INVALID_VISIBILITY'
    mock_document_service.list.assert_not_called()

# ** test: update_document_rejects_visibility_attribute
def test_update_document_rejects_visibility_attribute(mock_document_service):
    '''UpdateDocument still allows only title, status, category_id, and folder_id.'''

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            UpdateDocument,
            dependencies={'document_service': mock_document_service},
            id='doc-001',
            attribute='visibility',
            value='private',
        )
    assert exc_info.value.error_code == 'KB_INVALID_DOCUMENT_ATTRIBUTE'

# ** test: update_section_attributes_append_no_revision
@pytest.mark.parametrize('attribute,value', [
    ('heading_level', 3),
    ('icon', 'star'),
    ('content_type', 'text'),
])
def test_update_section_attributes_append_no_revision(mock_document_service, sample_section, attribute, value):
    '''Heading level, icon, and content type do not snapshot passages.'''

    mock_document_service.get_sections.return_value = [sample_section]

    DomainEvent.handle(
        UpdateDocumentSection,
        dependencies={'document_service': mock_document_service},
        id='sec-001',
        attribute=attribute,
        value=value,
        document_id='doc-001',
    )

    mock_document_service.append_section_revision.assert_not_called()
    mock_document_service.save_section.assert_called_once()

# ** test: update_document_appends_no_revision
def test_update_document_appends_no_revision(mock_document_service, sample_document):
    '''A header update is not section history.'''

    mock_document_service.get.return_value = sample_document

    DomainEvent.handle(
        UpdateDocument,
        dependencies={'document_service': mock_document_service},
        id='doc-001',
        attribute='title',
        value='Renamed',
    )

    mock_document_service.append_section_revision.assert_not_called()

# ** test: identical_content_write_does_not_save
def test_identical_content_write_does_not_save(mock_document_service, sample_section):
    '''An identical content write keeps stored identifiers and does not save.'''

    sample_section.set_paragraphs([
        Paragraph(
            id='kept-p',
            section_id='sec-001',
            position=0,
            block_type='normal',
            segments=[TextSegment(
                id='kept-s',
                position=0,
                text='Hello world',
                format_type='plain',
            )],
        ),
    ])
    updated_at = sample_section.updated_at
    mock_document_service.get_sections.return_value = [sample_section]

    result = DomainEvent.handle(
        UpdateDocumentSection,
        dependencies={'document_service': mock_document_service},
        id='sec-001',
        attribute='content',
        value='Hello world',
        document_id='doc-001',
    )

    assert result.paragraphs[0].id == 'kept-p'
    assert result.paragraphs[0].segments[0].id == 'kept-s'
    assert result.updated_at == updated_at
    mock_document_service.append_section_revision.assert_not_called()
    mock_document_service.save_section.assert_not_called()

# ** test: list_revisions_requires_document_id
def test_list_revisions_requires_document_id(mock_document_service):
    '''A missing document id raises and does not walk documents.'''

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            ListDocumentSectionRevisions,
            dependencies={'document_service': mock_document_service},
            id='sec-001',
        )

    assert exc_info.value.error_code == KB_DOCUMENT_SECTION_NOT_FOUND_ID
    mock_document_service.get_sections.assert_not_called()
    mock_document_service.list_section_revisions.assert_not_called()

# ** test: list_revisions_missing_section
def test_list_revisions_missing_section(mock_document_service):
    '''A missing section raises and does not list revisions.'''

    mock_document_service.get_sections.return_value = []

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            ListDocumentSectionRevisions,
            dependencies={'document_service': mock_document_service},
            id='missing',
            document_id='doc-001',
        )

    assert exc_info.value.error_code == KB_DOCUMENT_SECTION_NOT_FOUND_ID
    mock_document_service.list_section_revisions.assert_not_called()

# ** test: restore_missing_revision_does_not_write
def test_restore_missing_revision_does_not_write(mock_document_service, sample_section):
    '''A missing revision raises and does not append or save.'''

    mock_document_service.get_sections.return_value = [sample_section]
    mock_document_service.get_section_revision.return_value = None

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            RestoreDocumentSectionRevision,
            dependencies={'document_service': mock_document_service},
            id='sec-001',
            document_id='doc-001',
            number=4,
        )

    assert exc_info.value.error_code == KB_SECTION_REVISION_NOT_FOUND_ID
    mock_document_service.append_section_revision.assert_not_called()
    mock_document_service.save_section.assert_not_called()

# ** test: restore_non_positive_number
def test_restore_non_positive_number(mock_document_service, sample_section):
    '''A number less than 1 is a missing revision and writes nothing.'''

    mock_document_service.get_sections.return_value = [sample_section]

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            RestoreDocumentSectionRevision,
            dependencies={'document_service': mock_document_service},
            id='sec-001',
            document_id='doc-001',
            number=0,
        )

    assert exc_info.value.error_code == KB_SECTION_REVISION_NOT_FOUND_ID
    mock_document_service.get_section_revision.assert_not_called()
    mock_document_service.append_section_revision.assert_not_called()

# ** test: restore_puts_snapshot_paragraphs_back
def test_restore_puts_snapshot_paragraphs_back(mock_document_service, sample_section):
    '''Restore snapshots the current passages, then writes the chosen identifiers.'''

    sample_section.set_paragraphs([
        Paragraph(
            id='live-p',
            section_id='sec-001',
            position=0,
            block_type='normal',
            segments=[TextSegment(id='live-s', position=0, text='Live', format_type='plain')],
        ),
    ])
    sample_section.rename('Renamed')
    revision = SectionRevision(
        document_id='doc-001',
        section_id='sec-001',
        number=1,
        title='Original',
        content_type='code',
        created_at='2026-01-01T00:00:00+00:00',
        paragraphs=[
            Paragraph(
                id='old-p',
                section_id='sec-001',
                position=0,
                block_type='normal',
                segments=[TextSegment(id='old-s', position=0, text='Old', format_type='plain')],
            ),
        ],
    )
    mock_document_service.get_sections.return_value = [sample_section]
    mock_document_service.get_section_revision.return_value = revision

    result = DomainEvent.handle(
        RestoreDocumentSectionRevision,
        dependencies={'document_service': mock_document_service},
        id='sec-001',
        document_id='doc-001',
        number=1,
    )

    snapshot = mock_document_service.append_section_revision.call_args.kwargs
    assert snapshot['title'] == 'Renamed'
    assert snapshot['paragraphs'][0].segments[0].text == 'Live'
    assert snapshot['paragraphs'][0] is not sample_section.paragraphs[0]
    assert result.title == 'Renamed'
    assert result.content_type == 'markdown'
    assert result.paragraphs[0].id == 'old-p'
    assert result.paragraphs[0].segments[0].id == 'old-s'
    names = [call[0] for call in mock_document_service.mock_calls]
    assert names.index('append_section_revision') < names.index('save_section')
