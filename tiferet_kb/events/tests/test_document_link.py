"""tiferet_kb Document Link Event Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
import yaml
from unittest import mock

# ** app
from tiferet.assets import TiferetError
from tiferet.events import DomainEvent

from ...assets.core import (
    DOCUMENT_LINK_REFERENCES,
    DOCUMENT_LINK_RELATED_TO,
    DOCUMENT_LINK_SUPERSEDES,
)
from ...assets.errors import (
    DEFAULT_ERRORS,
    KB_DOCUMENT_LINK_ALREADY_EXISTS_ID,
    KB_DOCUMENT_NOT_FOUND_ID,
    KB_INVALID_DOCUMENT_LINK_ID,
)
from ...interfaces.document import DocumentService
from ...mappers.document_link import DocumentLinkTableObject
from ..document_link import AddDocumentLink, ListDocumentLinks, RemoveDocumentLink

# *** fixtures

# ** fixture: mock_document_service
@pytest.fixture
def mock_document_service() -> DocumentService:
    '''Mock DocumentService for link command tests.'''

    service = mock.Mock(spec=DocumentService)
    service.exists.return_value = True
    service.add_link.side_effect = lambda link: link
    service.list_links.return_value = []
    return service

# *** tests

# ** test: add_strips_type_and_derives_id
def test_add_strips_type_and_derives_id(mock_document_service):
    '''Add stores the stripped type and returns an id and created_at.'''

    result = DomainEvent.handle(
        AddDocumentLink,
        dependencies={'document_service': mock_document_service},
        source_id='doc-001',
        target_id='doc-002',
        link_type='  references  ',
        created_at='1999-01-01T00:00:00+00:00',
    )

    assert result.source_id == 'doc-001'
    assert result.target_id == 'doc-002'
    assert result.link_type == DOCUMENT_LINK_REFERENCES
    assert result.id
    assert result.created_at != '1999-01-01T00:00:00+00:00'
    mock_document_service.add_link.assert_called_once()

# ** test: add_keeps_documented_and_open_types
@pytest.mark.parametrize('link_type', [
    DOCUMENT_LINK_SUPERSEDES,
    DOCUMENT_LINK_RELATED_TO,
])
def test_add_keeps_documented_types(mock_document_service, link_type):
    '''The documented names are stored unchanged.'''

    result = DomainEvent.handle(
        AddDocumentLink,
        dependencies={'document_service': mock_document_service},
        source_id='doc-001',
        target_id='doc-002',
        link_type=link_type,
    )
    assert result.link_type == link_type

# ** test: add_missing_document_writes_nothing
@pytest.mark.parametrize('source_exists, target_exists', [
    (False, True),
    (True, False),
])
def test_add_missing_document_writes_nothing(mock_document_service, source_exists, target_exists):
    '''A missing endpoint fails with KB_DOCUMENT_NOT_FOUND and does not add.'''

    mock_document_service.exists.side_effect = lambda doc_id: (
        source_exists if doc_id == 'doc-001' else target_exists
    )

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            AddDocumentLink,
            dependencies={'document_service': mock_document_service},
            source_id='doc-001',
            target_id='doc-002',
            link_type='references',
        )
    assert exc_info.value.error_code == KB_DOCUMENT_NOT_FOUND_ID
    mock_document_service.add_link.assert_not_called()

# ** test: add_self_link_after_both_exist
def test_add_self_link_after_both_exist(mock_document_service):
    '''A self-link fails only after both documents exist.'''

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            AddDocumentLink,
            dependencies={'document_service': mock_document_service},
            source_id='doc-001',
            target_id='doc-001',
            link_type='related_to',
        )
    assert exc_info.value.error_code == KB_INVALID_DOCUMENT_LINK_ID
    mock_document_service.add_link.assert_not_called()

# ** test: add_rejects_empty_or_overlong_type
@pytest.mark.parametrize('link_type', ['', '   ', None, 'cites', 'References'])
def test_add_rejects_empty_type(mock_document_service, link_type):
    '''An empty or whitespace type is invalid and writes nothing.'''

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            AddDocumentLink,
            dependencies={'document_service': mock_document_service},
            source_id='doc-001',
            target_id='doc-002',
            link_type=link_type,
        )
    assert exc_info.value.error_code == KB_INVALID_DOCUMENT_LINK_ID
    mock_document_service.exists.assert_not_called()
    mock_document_service.add_link.assert_not_called()

# ** test: add_rejects_overlong_type_and_id
def test_add_rejects_overlong_type_and_id(mock_document_service):
    '''A type or id that does not fit the column is rejected, not clipped.'''

    overlong_type = 'x' * (DocumentLinkTableObject.type_width() + 1)
    overlong_id = 'i' * (DocumentLinkTableObject.identifier_width() + 1)

    with pytest.raises(TiferetError) as type_error:
        DomainEvent.handle(
            AddDocumentLink,
            dependencies={'document_service': mock_document_service},
            source_id='doc-001',
            target_id='doc-002',
            link_type=overlong_type,
        )
    assert type_error.value.error_code == KB_INVALID_DOCUMENT_LINK_ID

    with pytest.raises(TiferetError) as id_error:
        DomainEvent.handle(
            AddDocumentLink,
            dependencies={'document_service': mock_document_service},
            source_id='doc-001',
            target_id='doc-002',
            link_type='references',
            id=overlong_id,
        )
    assert id_error.value.error_code == KB_INVALID_DOCUMENT_LINK_ID
    mock_document_service.add_link.assert_not_called()

# ** test: list_directions_and_type_filter
def test_list_directions_and_type_filter(mock_document_service):
    '''Omitted direction is both. A type filter is passed through stripped.'''

    DomainEvent.handle(
        ListDocumentLinks,
        dependencies={'document_service': mock_document_service},
        document_id='doc-001',
    )
    mock_document_service.list_links.assert_called_with(
        'doc-001',
        direction='both',
        link_type=None,
    )

    DomainEvent.handle(
        ListDocumentLinks,
        dependencies={'document_service': mock_document_service},
        document_id='doc-001',
        direction='incoming',
        link_type='  cites  ',
    )
    mock_document_service.list_links.assert_called_with(
        'doc-001',
        direction='incoming',
        link_type='cites',
    )

# ** test: list_rejects_bad_direction_and_empty_type
@pytest.mark.parametrize('kwargs', [
    {'direction': 'sideways'},
    {'direction': ''},
    {'link_type': ''},
    {'link_type': '   '},
])
def test_list_rejects_bad_direction_and_empty_type(mock_document_service, kwargs):
    '''A bad direction or an empty type fails and does not list.'''

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            ListDocumentLinks,
            dependencies={'document_service': mock_document_service},
            document_id='doc-001',
            **kwargs,
        )
    assert exc_info.value.error_code == KB_INVALID_DOCUMENT_LINK_ID
    mock_document_service.list_links.assert_not_called()

# ** test: list_missing_document
def test_list_missing_document(mock_document_service):
    '''List fails when the document does not exist.'''

    mock_document_service.exists.return_value = False
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            ListDocumentLinks,
            dependencies={'document_service': mock_document_service},
            document_id='missing',
        )
    assert exc_info.value.error_code == KB_DOCUMENT_NOT_FOUND_ID
    mock_document_service.list_links.assert_not_called()

# ** test: remove_is_idempotent_at_the_event
def test_remove_is_idempotent_at_the_event(mock_document_service):
    '''Remove returns the id and does not require the row to exist.'''

    result = DomainEvent.handle(
        RemoveDocumentLink,
        dependencies={'document_service': mock_document_service},
        id='link-001',
    )
    assert result == 'link-001'
    mock_document_service.remove_link.assert_called_once_with('link-001')

# ** test: commands_and_errors_are_published
def test_commands_and_errors_are_published():
    '''The three commands are exported and the two error ids sit beside document-not-found.'''

    from ...events import AddDocumentLink as ExportedAdd
    from ...events import ListDocumentLinks as ExportedList
    from ...events import RemoveDocumentLink as ExportedRemove

    assert ExportedAdd is AddDocumentLink
    assert ExportedRemove is RemoveDocumentLink
    assert ExportedList is ListDocumentLinks
    assert KB_DOCUMENT_LINK_ALREADY_EXISTS_ID in DEFAULT_ERRORS
    assert KB_INVALID_DOCUMENT_LINK_ID in DEFAULT_ERRORS
    assert KB_DOCUMENT_NOT_FOUND_ID in DEFAULT_ERRORS

    root = Path(__file__).resolve().parents[3]
    features = yaml.safe_load((root / 'app/configs/feature.yml').read_text())
    container = yaml.safe_load((root / 'app/configs/container.yml').read_text())
    errors = yaml.safe_load((root / 'app/configs/error.yml').read_text())

    group = features['features']['document_link']
    assert set(group) == {'add', 'remove', 'list'}
    assert group['add']['commands'][0]['attribute_id'] == 'add_document_link_event'
    assert group['remove']['commands'][0]['attribute_id'] == 'remove_document_link_event'
    assert group['list']['commands'][0]['attribute_id'] == 'list_document_links_event'
    assert container['attrs']['add_document_link_event']['class_name'] == 'AddDocumentLink'
    assert container['attrs']['remove_document_link_event']['class_name'] == 'RemoveDocumentLink'
    assert container['attrs']['list_document_links_event']['class_name'] == 'ListDocumentLinks'
    assert 'kb_document_not_found' in errors['errors']
    assert 'kb_document_link_already_exists' in errors['errors']
    assert 'kb_invalid_document_link' in errors['errors']
