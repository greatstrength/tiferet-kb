"""tiferet_kb — Knowledge Base Extension for the Tiferet Framework"""

# *** exports

# ** app
# Wrap runtime imports in a try/except so that build tools can import
# __version__ without requiring the full dependency tree to be installed.
try:
    from . import assets as a
    from .domain import Category, Document, DocumentSection, SectionComment, EmbeddingRecord, TextSegment, Paragraph, Template, TemplateSection, Folder, Tag
    from .interfaces import CategoryService, DocumentService, TemplateService, FolderService, TagService
    from .mappers import (
        CategoryAggregate,
        CategoryNodeObject,
        DocumentAggregate,
        DocumentSectionAggregate,
        DocumentTableObject,
        DocumentSectionNodeObject,
        SectionCommentAggregate,
        SectionCommentTableObject,
        HybridSegmentTableObject,
        EmbeddingRecordAggregate,
        TemplateAggregate,
        TemplateSectionAggregate,
        TemplateTableObject,
        TemplateSectionTableObject,
        FolderAggregate,
        FolderNodeObject,
        TagAggregate,
        TagNodeObject,
    )
    from .events import (
        EmbedDocumentSections,
        SearchSimilarSections,
        RemoveEmbedding,
        ImportMarkdownDocument,
        ExportDocumentMarkdown,
    )
except Exception as e:
    import os, sys
    if not os.getenv('TIFERET_KB_SILENT_IMPORTS'):
        print(f'Warning: Failed to import tiferet_kb modules: {e}', file=sys.stderr)

# *** version

__version__ = '1.0.0a1'
