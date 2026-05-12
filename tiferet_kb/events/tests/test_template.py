"""tiferet_kb Template Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events import DomainEvent
from tiferet.assets import TiferetError

from ...interfaces.template import TemplateService
from ...interfaces.document import DocumentService
from ...mappers.template import TemplateAggregate, TemplateSectionAggregate
from ..template import (
    AddTemplate,
    GetTemplate,
    ListTemplates,
    UpdateTemplate,
    RemoveTemplate,
    ApplyTemplate,
)

# *** fixtures

# ** fixture: mock_template_service
@pytest.fixture
def mock_template_service() -> TemplateService:
    '''Mock TemplateService for testing.'''
    return mock.Mock(spec=TemplateService)


# ** fixture: mock_document_service
@pytest.fixture
def mock_document_service() -> DocumentService:
    '''Mock DocumentService for testing.'''
    return mock.Mock(spec=DocumentService)


# ** fixture: sample_template
@pytest.fixture
def sample_template() -> TemplateAggregate:
    '''Sample TemplateAggregate with sections.'''
    tmpl = TemplateAggregate(
        id='tmpl-001',
        name='Meeting Notes',
        description='For meetings',
        category_id='meetings',
        created_at='2026-01-01T00:00:00+00:00',
        updated_at='2026-01-01T00:00:00+00:00',
    )
    tmpl.sections = [
        TemplateSectionAggregate(
            id='tsec-001', template_id='tmpl-001', title='Agenda',
            content_type='markdown', default_content='## Agenda', position=0,
        ),
        TemplateSectionAggregate(
            id='tsec-002', template_id='tmpl-001', title='Action Items',
            content_type='text', default_content='', position=1,
        ),
    ]
    return tmpl

# *** tests

# ** test: add_template_success
def test_add_template_success(mock_template_service):
    '''Test successful creation of a new template.'''

    mock_template_service.exists.return_value = False

    result = DomainEvent.handle(
        AddTemplate,
        dependencies={'template_service': mock_template_service},
        name='Sprint Retro',
    )

    assert result.name == 'Sprint Retro'
    assert result.id is not None
    mock_template_service.save.assert_called_once()


# ** test: add_template_with_sections
def test_add_template_with_sections(mock_template_service):
    '''Test creating a template with initial sections.'''

    mock_template_service.exists.return_value = False

    result = DomainEvent.handle(
        AddTemplate,
        dependencies={'template_service': mock_template_service},
        name='Sprint Retro',
        sections=[
            {'title': 'What went well', 'content_type': 'markdown'},
            {'title': 'What to improve', 'content_type': 'text', 'default_content': '- '},
        ],
    )

    assert result.name == 'Sprint Retro'
    assert mock_template_service.save_section.call_count == 2


# ** test: add_template_duplicate
def test_add_template_duplicate(mock_template_service):
    '''Test that adding a duplicate template raises.'''

    mock_template_service.exists.return_value = True

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddTemplate,
            dependencies={'template_service': mock_template_service},
            name='Duplicate',
            id='existing',
        )


# ** test: get_template_success
def test_get_template_success(mock_template_service, sample_template):
    '''Test successful retrieval.'''

    mock_template_service.get.return_value = sample_template

    result = DomainEvent.handle(
        GetTemplate,
        dependencies={'template_service': mock_template_service},
        id='tmpl-001',
    )

    assert result is sample_template


# ** test: get_template_not_found
def test_get_template_not_found(mock_template_service):
    '''Test not-found raises.'''

    mock_template_service.get.return_value = None

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            GetTemplate,
            dependencies={'template_service': mock_template_service},
            id='nonexistent',
        )


# ** test: list_templates_success
def test_list_templates_success(mock_template_service, sample_template):
    '''Test listing templates.'''

    mock_template_service.list.return_value = [sample_template]

    result = DomainEvent.handle(
        ListTemplates,
        dependencies={'template_service': mock_template_service},
    )

    assert len(result) == 1


# ** test: update_template_success
def test_update_template_success(mock_template_service, sample_template):
    '''Test successful template update.'''

    mock_template_service.get.return_value = sample_template

    result = DomainEvent.handle(
        UpdateTemplate,
        dependencies={'template_service': mock_template_service},
        id='tmpl-001',
        attribute='name',
        value='Updated Template',
    )

    assert result.name == 'Updated Template'
    mock_template_service.save.assert_called()


# ** test: update_template_invalid_attribute
def test_update_template_invalid_attribute(mock_template_service):
    '''Test invalid attribute raises.'''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            UpdateTemplate,
            dependencies={'template_service': mock_template_service},
            id='tmpl-001',
            attribute='nonexistent',
            value='bad',
        )


# ** test: remove_template_success
def test_remove_template_success(mock_template_service):
    '''Test successful removal.'''

    result = DomainEvent.handle(
        RemoveTemplate,
        dependencies={'template_service': mock_template_service},
        id='tmpl-001',
    )

    assert result == 'tmpl-001'
    mock_template_service.delete.assert_called_once_with('tmpl-001')


# ** test: apply_template_success
def test_apply_template_success(mock_template_service, mock_document_service, sample_template):
    '''Test applying a template creates a document with stamped sections.'''

    mock_template_service.get.return_value = sample_template

    result = DomainEvent.handle(
        ApplyTemplate,
        dependencies={
            'template_service': mock_template_service,
            'document_service': mock_document_service,
        },
        template_id='tmpl-001',
        title='Sprint 42 Retro',
    )

    # Document should have the template's category.
    assert result.title == 'Sprint 42 Retro'
    assert result.template_id == 'tmpl-001'
    assert result.category_id == 'meetings'

    # Document header saved once + 2 sections saved.
    mock_document_service.save.assert_called_once()
    assert mock_document_service.save_section.call_count == 2


# ** test: apply_template_not_found
def test_apply_template_not_found(mock_template_service, mock_document_service):
    '''Test that applying a non-existent template raises.'''

    mock_template_service.get.return_value = None

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            ApplyTemplate,
            dependencies={
                'template_service': mock_template_service,
                'document_service': mock_document_service,
            },
            template_id='nonexistent',
            title='Test',
        )
