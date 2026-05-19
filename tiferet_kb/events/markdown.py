"""tiferet_kb Markdown Events"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from tiferet.events import DomainEvent

from ..assets import constants as const
from ..domain.document import Document, DocumentSection
from ..interfaces.document import DocumentService
from ..mappers.document import DocumentAggregate, DocumentSectionAggregate
from ..utils.markdown import (
    split_markdown_sections,
    join_markdown_sections,
    parse_content_to_paragraphs,
)

# *** events

# ** event: import_markdown_document
class ImportMarkdownDocument(DomainEvent):
    '''
    Event to import a markdown string as a new document with sections.

    Convention: the markdown must start with an ``# H1`` heading.
    Each H1 heading delimits a new document section. The first H1's
    text becomes the document title; subsequent H1 headings create
    additional sections.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the ImportMarkdownDocument event.

        :param document_service: The document service for persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['content'])
    def execute(self,
            content: str,
            category_id: str | None = None,
            folder_id: str | None = None,
            template_id: str | None = None,
            **kwargs,
        ) -> Document:
        '''
        Import a markdown document.

        :param content: The raw markdown string (must start with ``# H1``).
        :type content: str
        :param category_id: Optional category identifier.
        :type category_id: str | None
        :param folder_id: Optional folder identifier.
        :type folder_id: str | None
        :param template_id: Optional template identifier.
        :type template_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created document with sections populated.
        :rtype: Document
        '''

        # Parse the markdown into sections.
        try:
            raw_sections = split_markdown_sections(content)
        except ValueError as e:
            self.raise_error(
                error_code=const.KB_INVALID_CONTENT_TYPE_ID,
                message=str(e),
                content_type='markdown',
            )

        # Verify at least one section was parsed.
        self.verify(
            expression=len(raw_sections) > 0,
            error_code=const.KB_INVALID_CONTENT_TYPE_ID,
            message='Markdown content produced no sections.',
            content_type='markdown',
        )

        # Use the first section's title as the document title.
        doc_title = raw_sections[0]['title']

        # Build the document aggregate.
        doc_kwargs = dict(title=doc_title)
        if category_id:
            doc_kwargs['category_id'] = category_id
        if folder_id:
            doc_kwargs['folder_id'] = folder_id
        if template_id:
            doc_kwargs['template_id'] = template_id

        document = DocumentAggregate(**doc_kwargs)

        # Persist the document header.
        self.document_service.save(document)

        # Create and persist each section.
        sections: List[DocumentSectionAggregate] = []
        for position, raw in enumerate(raw_sections):
            section = DocumentSectionAggregate(
                document_id=document.id,
                title=raw['title'],
                content_type='markdown',
                heading_level=1,
                position=position,
            )

            # Parse markdown content into paragraphs with segments.
            if raw['content']:
                paragraphs = parse_content_to_paragraphs(raw['content'], section.id)
                section.set_paragraphs(paragraphs)

            # Persist the section.
            self.document_service.save_section(section)
            sections.append(section)

        # Attach sections to the document.
        document.sections = sections

        # Return the assembled document.
        return document


# ** event: export_document_markdown
class ExportDocumentMarkdown(DomainEvent):
    '''
    Event to export a document and its sections as a markdown string.

    Sections are emitted in position order, each as an ``# H1`` heading
    followed by its content.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the ExportDocumentMarkdown event.

        :param document_service: The document service for retrieval.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Export a document to markdown.

        :param id: The document identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The markdown string.
        :rtype: str
        '''

        # Retrieve the document with sections.
        document = self.document_service.get(id)

        # Verify the document exists.
        self.verify(
            expression=document is not None,
            error_code=const.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=id,
        )

        # Sort sections by position.
        ordered_sections = sorted(document.sections, key=lambda s: s.position)

        # Build section dicts for join_markdown_sections.
        section_dicts = []
        for section in ordered_sections:

            # Reconstruct content from paragraphs if available.
            content = self._reconstruct_content(section)
            section_dicts.append({
                'title': section.title,
                'content': content,
            })

        # Join sections into markdown.
        return join_markdown_sections(section_dicts)

    # * method: _reconstruct_content
    def _reconstruct_content(self, section) -> str:
        '''
        Reconstruct plain markdown content from a section's paragraphs.

        If the section has no paragraphs, returns an empty string.

        :param section: The document section.
        :return: The reconstructed markdown content.
        :rtype: str
        '''

        if not section.paragraphs:
            return ''

        from ..utils.markdown import reassemble_paragraph

        parts: List[str] = []
        for para in sorted(section.paragraphs, key=lambda p: p.position):

            if para.block_type == 'code_block':
                # Reconstruct fenced code block.
                text = para.segments[0].text if para.segments else ''
                parts.append(f'```\n{text}\n```')

            elif para.block_type == 'quote':
                # Reconstruct quote block.
                text = reassemble_paragraph(para.segments)
                lines = text.split('\n')
                parts.append('\n'.join(f'> {line}' for line in lines))

            else:
                # Normal paragraph.
                parts.append(reassemble_paragraph(para.segments))

        return '\n\n'.join(parts)
