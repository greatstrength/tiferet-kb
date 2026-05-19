"""tiferet_kb Markdown Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events import DomainEvent
from tiferet.assets import TiferetError

from ...interfaces import DocumentService
from ...mappers import DocumentAggregate, DocumentSectionAggregate
from ..markdown import ImportMarkdownDocument, ExportDocumentMarkdown

# *** fixtures

# ** fixture: mock_document_service
@pytest.fixture
def mock_document_service() -> DocumentService:
    '''
    Mock DocumentService for testing.
    '''
    return mock.Mock(spec=DocumentService)


# ** fixture: sample_markdown
@pytest.fixture
def sample_markdown() -> str:
    '''
    Sample markdown document with two H1 sections.
    '''
    return (
        '# Introduction\n\n'
        'Welcome to the knowledge base.\n\n'
        '# Getting Started\n\n'
        'Follow these steps to begin.'
    )


# *** tests: import_markdown_document

# ** test: import_markdown_success
def test_import_markdown_success(mock_document_service: DocumentService, sample_markdown: str):
    '''
    Test successful markdown import creates a document with sections.
    '''

    # Execute via DomainEvent.handle.
    result = DomainEvent.handle(
        ImportMarkdownDocument,
        dependencies={'document_service': mock_document_service},
        content=sample_markdown,
        category_id='notes',
    )

    # Assert the document title comes from the first H1.
    assert result.title == 'Introduction'
    assert result.category_id == 'notes'

    # Assert two sections were created.
    assert len(result.sections) == 2
    assert result.sections[0].title == 'Introduction'
    assert result.sections[0].position == 0
    assert result.sections[1].title == 'Getting Started'
    assert result.sections[1].position == 1

    # Assert the document and sections were persisted.
    mock_document_service.save.assert_called_once()
    assert mock_document_service.save_section.call_count == 2


# ** test: import_markdown_single_section
def test_import_markdown_single_section(mock_document_service: DocumentService):
    '''
    Test import of a markdown document with a single section.
    '''

    content = '# Solo Section\n\nJust one section here.'

    result = DomainEvent.handle(
        ImportMarkdownDocument,
        dependencies={'document_service': mock_document_service},
        content=content,
    )

    assert result.title == 'Solo Section'
    assert len(result.sections) == 1
    assert result.sections[0].paragraphs  # Content was parsed


# ** test: import_markdown_no_h1_raises
def test_import_markdown_no_h1_raises(mock_document_service: DocumentService):
    '''
    Test that markdown without an H1 heading raises an error.
    '''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            ImportMarkdownDocument,
            dependencies={'document_service': mock_document_service},
            content='No heading here, just text.',
        )


# ** test: import_markdown_missing_content
def test_import_markdown_missing_content(mock_document_service: DocumentService):
    '''
    Test that missing content parameter raises an error.
    '''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            ImportMarkdownDocument,
            dependencies={'document_service': mock_document_service},
        )


# *** tests: export_document_markdown

# ** test: export_markdown_success
def test_export_markdown_success(mock_document_service: DocumentService):
    '''
    Test successful export of a document to markdown.
    '''

    # Build a mock document with sections.
    section1 = DocumentSectionAggregate(
        document_id='doc-1',
        title='Overview',
        content_type='markdown',
        position=0,
    )
    section2 = DocumentSectionAggregate(
        document_id='doc-1',
        title='Details',
        content_type='markdown',
        position=1,
    )
    doc = DocumentAggregate(id='doc-1', title='Overview')
    doc.sections = [section1, section2]

    # Arrange the service to return the document.
    mock_document_service.get.return_value = doc

    # Execute via DomainEvent.handle.
    result = DomainEvent.handle(
        ExportDocumentMarkdown,
        dependencies={'document_service': mock_document_service},
        id='doc-1',
    )

    # Assert the markdown contains both section headings.
    assert '# Overview' in result
    assert '# Details' in result
    mock_document_service.get.assert_called_once_with('doc-1')


# ** test: export_markdown_not_found
def test_export_markdown_not_found(mock_document_service: DocumentService):
    '''
    Test that exporting a non-existent document raises an error.
    '''

    # Arrange the service to return None.
    mock_document_service.get.return_value = None

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            ExportDocumentMarkdown,
            dependencies={'document_service': mock_document_service},
            id='nonexistent',
        )
