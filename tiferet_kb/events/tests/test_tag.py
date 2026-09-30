"""tiferet_kb Tag Event Tests"""

# *** imports

# ** core
import inspect

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events import DomainEvent
from tiferet.assets import TiferetError

from ...assets import errors as err
from ...domain.document import Document
from ...interfaces.document import DocumentService
from ...interfaces.tag import TagService
from ...mappers.tag import TagAggregate
from ..document import AddDocument, AddDocumentSection, ListDocuments, UpdateDocument
from ..embedding import SearchSimilarSections
from ..markdown import ImportMarkdownDocument
from ..tag import (
    AddTag,
    GetTag,
    ListTags,
    UpdateTag,
    RemoveTag,
    TagDocument,
    UntagDocument,
    ListDocumentTags,
)
from ..template import ApplyTemplate

# *** fixtures

# ** fixture: mock_tag_service
@pytest.fixture
def mock_tag_service() -> TagService:
    '''
    Mock TagService for testing.
    '''
    return mock.Mock(spec=TagService)

# ** fixture: mock_document_service
@pytest.fixture
def mock_document_service() -> DocumentService:
    '''
    Mock DocumentService for testing.
    '''
    return mock.Mock(spec=DocumentService)

# ** fixture: sample_tag
@pytest.fixture
def sample_tag() -> TagAggregate:
    '''
    Sample TagAggregate instance for testing.
    '''
    return TagAggregate(id='release', name='Release', color='#3B82F6')

# *** tests

# ** test: add_tag_success
def test_add_tag_success(mock_tag_service: TagService):
    '''
    AddTag with an id and a name creates a tag. Color may be omitted.
    '''

    # Arrange the service to report no existing tag.
    mock_tag_service.exists.return_value = False

    # Execute via DomainEvent.handle.
    result = DomainEvent.handle(
        AddTag,
        dependencies={'tag_service': mock_tag_service},
        id='My-Tag',
        name='Release',
    )

    # Assert the id is stored as given and color is absent.
    assert result.id == 'My-Tag'
    assert result.name == 'Release'
    assert result.color is None
    mock_tag_service.save.assert_called_once()

# ** test: add_tag_duplicate
def test_add_tag_duplicate(mock_tag_service: TagService):
    '''
    A second AddTag with the same id raises KB_TAG_ALREADY_EXISTS.
    '''

    # Arrange the service to report an existing tag.
    mock_tag_service.exists.return_value = True

    # Execute and expect the duplicate-id error.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            AddTag,
            dependencies={'tag_service': mock_tag_service},
            id='release',
            name='Release',
        )
    assert exc_info.value.error_code == err.KB_TAG_ALREADY_EXISTS_ID
    mock_tag_service.save.assert_not_called()

# ** test: add_tag_allows_shared_name
def test_add_tag_allows_shared_name(mock_tag_service: TagService):
    '''
    Two tags may share a display name. Uniqueness is the id.
    '''

    # Arrange the service to accept the new id.
    mock_tag_service.exists.return_value = False

    # Execute with a name another tag could already use.
    result = DomainEvent.handle(
        AddTag,
        dependencies={'tag_service': mock_tag_service},
        id='release-2',
        name='Release',
    )
    assert result.name == 'Release'

# ** test: get_tag_not_found
def test_get_tag_not_found(mock_tag_service: TagService):
    '''
    GetTag of an unknown id raises KB_TAG_NOT_FOUND.
    '''

    # Arrange the service to return None.
    mock_tag_service.get.return_value = None

    # Execute and expect the not-found error.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            GetTag,
            dependencies={'tag_service': mock_tag_service},
            id='missing',
        )
    assert exc_info.value.error_code == err.KB_TAG_NOT_FOUND_ID

# ** test: list_tags_includes_tag
def test_list_tags_includes_tag(mock_tag_service: TagService, sample_tag: TagAggregate):
    '''
    ListTags returns every tag and takes no filter.
    '''

    # Arrange the service to return the sample tag.
    mock_tag_service.list.return_value = [sample_tag]

    # Execute via DomainEvent.handle.
    result = DomainEvent.handle(
        ListTags,
        dependencies={'tag_service': mock_tag_service},
    )
    assert result == [sample_tag]
    mock_tag_service.list.assert_called_once_with()

# ** test: update_tag_name_and_clear_color
def test_update_tag_name_and_clear_color(mock_tag_service: TagService, sample_tag: TagAggregate):
    '''
    UpdateTag can change name and can clear color.
    '''

    # Arrange the service to return the sample tag.
    mock_tag_service.get.return_value = sample_tag

    # Rename the tag.
    renamed = DomainEvent.handle(
        UpdateTag,
        dependencies={'tag_service': mock_tag_service},
        id='release',
        attribute='name',
        value='Ship',
    )
    assert renamed.name == 'Ship'

    # Clear the color.
    cleared = DomainEvent.handle(
        UpdateTag,
        dependencies={'tag_service': mock_tag_service},
        id='release',
        attribute='color',
        value=None,
    )
    assert cleared.color is None

# ** test: update_tag_rejects_id
def test_update_tag_rejects_id(mock_tag_service: TagService):
    '''
    UpdateTag raises KB_INVALID_TAG_ATTRIBUTE for id and any other attribute.
    '''

    # Execute with the id attribute.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            UpdateTag,
            dependencies={'tag_service': mock_tag_service},
            id='release',
            attribute='id',
            value='other',
        )
    assert exc_info.value.error_code == err.KB_INVALID_TAG_ATTRIBUTE_ID
    mock_tag_service.get.assert_not_called()

# ** test: update_tag_rejects_empty_name
def test_update_tag_rejects_empty_name(mock_tag_service: TagService):
    '''
    A name update requires a non-empty string.
    '''

    # Execute with a blank name.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            UpdateTag,
            dependencies={'tag_service': mock_tag_service},
            id='release',
            attribute='name',
            value='   ',
        )
    assert exc_info.value.error_code == err.KB_INVALID_TAG_ATTRIBUTE_ID

# ** test: tag_document_missing_document_writes_nothing
def test_tag_document_missing_document_writes_nothing(mock_document_service, mock_tag_service):
    '''
    TagDocument raises KB_DOCUMENT_NOT_FOUND and writes no association.
    '''

    # Arrange a missing document.
    mock_document_service.exists.return_value = False

    # Execute and expect the document error before the tag is consulted.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            TagDocument,
            dependencies={
                'document_service': mock_document_service,
                'tag_service': mock_tag_service,
            },
            document_id='missing',
            tag_id='release',
        )
    assert exc_info.value.error_code == err.KB_DOCUMENT_NOT_FOUND_ID
    mock_tag_service.get.assert_not_called()
    mock_tag_service.tag_document.assert_not_called()

# ** test: tag_document_missing_tag_writes_nothing
def test_tag_document_missing_tag_writes_nothing(mock_document_service, mock_tag_service):
    '''
    TagDocument raises KB_TAG_NOT_FOUND and writes no association.
    '''

    # Arrange a present document and a missing tag.
    mock_document_service.exists.return_value = True
    mock_tag_service.get.return_value = None

    # Execute and expect the tag error.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            TagDocument,
            dependencies={
                'document_service': mock_document_service,
                'tag_service': mock_tag_service,
            },
            document_id='doc-1',
            tag_id='missing',
        )
    assert exc_info.value.error_code == err.KB_TAG_NOT_FOUND_ID
    mock_tag_service.tag_document.assert_not_called()

# ** test: tag_document_repeat_is_one_call
def test_tag_document_records_pair(mock_document_service, mock_tag_service, sample_tag):
    '''
    TagDocument records the pair after both ids exist.
    '''

    # Arrange both sides present.
    mock_document_service.exists.return_value = True
    mock_tag_service.get.return_value = sample_tag

    # Execute.
    result = DomainEvent.handle(
        TagDocument,
        dependencies={
            'document_service': mock_document_service,
            'tag_service': mock_tag_service,
        },
        document_id='doc-1',
        tag_id='release',
    )
    assert result == 'doc-1'
    mock_tag_service.tag_document.assert_called_once_with('doc-1', 'release')
    mock_document_service.get.assert_not_called()

# ** test: untag_document_absent_succeeds
def test_untag_document_absent_succeeds(mock_tag_service):
    '''
    UntagDocument succeeds when the pair was never tagged.
    '''

    # Execute. The service call is idempotent.
    result = DomainEvent.handle(
        UntagDocument,
        dependencies={'tag_service': mock_tag_service},
        document_id='doc-1',
        tag_id='gone',
    )
    assert result == 'doc-1'
    mock_tag_service.untag_document.assert_called_once_with('doc-1', 'gone')
    mock_tag_service.delete.assert_not_called()

# ** test: list_documents_tag_filter_intersects
def test_list_documents_tag_filter_intersects(mock_document_service, mock_tag_service):
    '''
    ListDocuments(tag_id=T) returns only carriers and still AND-s header filters.
    '''

    # Arrange two headers, only one of which carries the tag.
    carried = mock.Mock(id='doc-1', sections=[])
    other = mock.Mock(id='doc-2', sections=[])
    mock_document_service.list.return_value = [carried, other]
    mock_tag_service.list_document_ids.return_value = ['doc-1', 'doc-1']

    # Execute with every header filter plus the tag.
    result = DomainEvent.handle(
        ListDocuments,
        dependencies={
            'document_service': mock_document_service,
            'tag_service': mock_tag_service,
        },
        folder_id='folder-1',
        category_id='notes',
        status='draft',
        tag_id='release',
    )

    # Assert the intersection, and that tag_id was not a header query.
    assert result == [carried]
    mock_document_service.list.assert_called_once_with(
        folder_id='folder-1',
        category_id='notes',
        status='draft',
        title=None,
        include_properties=False,
        property_name=None,
        property_value=None,
        property_value_type=None,
        visibility=None,
        owner_id=None,
    )
    mock_tag_service.list_document_ids.assert_called_once_with('release')

# ** test: list_documents_unknown_tag_is_empty
def test_list_documents_unknown_tag_is_empty(mock_document_service, mock_tag_service):
    '''
    A tag_id that matches nothing yields an empty list, not KB_TAG_NOT_FOUND.
    '''

    # Arrange a header list and no carriers.
    mock_document_service.list.return_value = [mock.Mock(id='doc-1')]
    mock_tag_service.list_document_ids.return_value = []

    # Execute.
    result = DomainEvent.handle(
        ListDocuments,
        dependencies={
            'document_service': mock_document_service,
            'tag_service': mock_tag_service,
        },
        tag_id='missing',
    )
    assert result == []

# ** test: list_documents_empty_tag_id_skips_association
def test_list_documents_empty_tag_id_skips_association(mock_document_service, mock_tag_service):
    '''
    An empty tag_id is no tag condition, so untagged documents remain.
    '''

    # Arrange an untagged header.
    untagged = mock.Mock(id='doc-1')
    mock_document_service.list.return_value = [untagged]

    # Execute with an empty tag id.
    result = DomainEvent.handle(
        ListDocuments,
        dependencies={
            'document_service': mock_document_service,
            'tag_service': mock_tag_service,
        },
        tag_id='',
    )
    assert result == [untagged]
    mock_tag_service.list_document_ids.assert_not_called()

# ** test: update_document_rejects_tag_attributes
def test_update_document_rejects_tag_attributes(mock_document_service):
    '''
    UpdateDocument with tag_id or tags still raises KB_INVALID_DOCUMENT_ATTRIBUTE.
    '''

    # Both names stay outside the header allowlist.
    for attribute in ('tag_id', 'tags'):
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                UpdateDocument,
                dependencies={'document_service': mock_document_service},
                id='doc-1',
                attribute=attribute,
                value='release',
            )
        assert exc_info.value.error_code == err.KB_INVALID_DOCUMENT_ATTRIBUTE_ID
    mock_document_service.get.assert_not_called()

# ** test: add_document_ignores_tag_kwargs
def test_add_document_ignores_tag_kwargs(mock_document_service):
    '''
    AddDocument does not gain a tags parameter. Extra kwargs are not written.
    '''

    # Arrange a fresh document.
    mock_document_service.exists.return_value = False

    # Execute with tag kwargs the event must ignore.
    result = DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': mock_document_service},
        title='Notes',
        tags=['release'],
        tag_id='release',
    )
    assert result.category_id is None
    assert 'tags' not in type(result).model_fields

# ** test: list_document_tags_missing_document
def test_list_document_tags_missing_document(mock_document_service, mock_tag_service):
    '''
    ListDocumentTags raises KB_DOCUMENT_NOT_FOUND when the document is missing.
    '''

    # Arrange a missing document.
    mock_document_service.exists.return_value = False

    # Execute and expect the document error.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            ListDocumentTags,
            dependencies={
                'document_service': mock_document_service,
                'tag_service': mock_tag_service,
            },
            document_id='missing',
        )
    assert exc_info.value.error_code == err.KB_DOCUMENT_NOT_FOUND_ID
    mock_tag_service.list_tags_for_document.assert_not_called()

# ** test: list_document_tags_empty
def test_list_document_tags_empty(mock_document_service, mock_tag_service):
    '''
    An existing document that carries no tags returns an empty list.
    '''

    # Arrange an existing untagged document.
    mock_document_service.exists.return_value = True
    mock_tag_service.list_tags_for_document.return_value = []

    # Execute.
    result = DomainEvent.handle(
        ListDocumentTags,
        dependencies={
            'document_service': mock_document_service,
            'tag_service': mock_tag_service,
        },
        document_id='doc-1',
    )
    assert result == []

# ** test: remove_tag_in_use
def test_remove_tag_in_use(mock_tag_service):
    '''
    RemoveTag raises KB_TAG_IN_USE and does not delete while a document carries it.
    '''

    # Arrange a carrier.
    mock_tag_service.list_document_ids.return_value = ['doc-1']

    # Execute and expect the in-use error.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            RemoveTag,
            dependencies={'tag_service': mock_tag_service},
            id='release',
        )
    assert exc_info.value.error_code == err.KB_TAG_IN_USE_ID
    mock_tag_service.delete.assert_not_called()

# ** test: remove_tag_absent_succeeds
def test_remove_tag_absent_succeeds(mock_tag_service):
    '''
    RemoveTag of an id no document carries succeeds even when the tag is gone.
    '''

    # Arrange no carriers.
    mock_tag_service.list_document_ids.return_value = []

    # Execute. Existence is not checked.
    result = DomainEvent.handle(
        RemoveTag,
        dependencies={'tag_service': mock_tag_service},
        id='missing',
    )
    assert result == 'missing'
    mock_tag_service.delete.assert_called_once_with('missing')
    mock_tag_service.get.assert_not_called()

# ** test: remove_document_clears_before_delete
def test_remove_document_clears_before_delete(mock_document_service, mock_tag_service):
    '''
    RemoveDocument clears associations before it deletes the document.
    '''

    # Record call order.
    order = []
    mock_tag_service.clear_document.side_effect = lambda document_id: order.append('clear')
    mock_document_service.delete.side_effect = lambda document_id: order.append('delete')

    # Execute.
    from ..document import RemoveDocument
    result = DomainEvent.handle(
        RemoveDocument,
        dependencies={
            'document_service': mock_document_service,
            'tag_service': mock_tag_service,
        },
        id='doc-1',
    )
    assert result == 'doc-1'
    assert order == ['clear', 'delete']

# ** test: out_of_scope_events_gain_no_tag_parameter
def test_out_of_scope_events_gain_no_tag_parameter():
    '''
    ApplyTemplate, section write, markdown import, and search_similar gain no tag parameter.
    '''

    # Assert none of those execute methods accepted a tag argument.
    for event_cls in (
        ApplyTemplate,
        AddDocumentSection,
        ImportMarkdownDocument,
        SearchSimilarSections,
    ):
        params = inspect.signature(event_cls.execute).parameters
        assert 'tag_id' not in params
        assert 'tags' not in params

# ** test: document_model_has_no_tags_field
def test_document_model_has_no_tags_field():
    '''
    Document has no tags field and no content field.
    '''

    # Assert the header model.
    assert 'tags' not in Document.model_fields
    assert 'content' not in Document.model_fields
