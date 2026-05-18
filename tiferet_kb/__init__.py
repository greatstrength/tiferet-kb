"""tiferet_kb — Knowledge Base Extension for the Tiferet Framework"""

# *** exports

# ** app
# Wrap runtime imports in a try/except so that build tools can import
# __version__ without requiring the full dependency tree to be installed.
try:
    from .domain import Category, Document, DocumentSection, EmbeddingRecord, TextSegment, Paragraph, Template, TemplateSection, Folder
    from .interfaces import CategoryService, DocumentService, TemplateService, FolderService
    from .mappers import (
        CategoryAggregate,
        CategoryNodeObject,
        DocumentAggregate,
        DocumentSectionAggregate,
        DocumentTableObject,
        DocumentSectionNodeObject,
        HybridSegmentTableObject,
        EmbeddingRecordAggregate,
        TemplateAggregate,
        TemplateSectionAggregate,
        TemplateTableObject,
        TemplateSectionTableObject,
        FolderAggregate,
        FolderNodeObject,
    )
    from .events import (
        EmbedDocumentSections,
        SearchSimilarSections,
        RemoveEmbedding,
    )
except Exception as e:
    import os, sys
    if not os.getenv('TIFERET_KB_SILENT_IMPORTS'):
        print(f'Warning: Failed to import tiferet_kb modules: {e}', file=sys.stderr)

# *** version

__version__ = '1.0.0b2'
