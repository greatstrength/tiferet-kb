"""tiferet_kb — Knowledge Base Extension for the Tiferet Framework"""

# *** constants

# ** constant: silent_imports
SILENT_IMPORTS = 'TIFERET_KB_SILENT_IMPORTS'

# *** functions

# ** function: __getattr__
def __getattr__(name: str):
    '''
    Load the session client when the caller asks for KB.

    :param name: The attribute name.
    :type name: str
    :return: The session client function when the name is KB.
    :rtype: object
    '''

    # Load the client only for the public name.
    if name == 'KB':
        from .blueprints.kb import build_kb
        return build_kb

    # Any other missing name is a real attribute error.
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

# *** exports

# ** app
# Wrap runtime imports in a try/except so that build tools can import
# __version__ without requiring the full dependency tree to be installed.
try:
    from . import assets as a
    from .domain import Category, Document, DocumentSection, SectionRevision, DocumentLink, SectionComment, EmbeddingRecord, TextSegment, Paragraph, Template, TemplateSection, Folder, Tag
    from .interfaces import CategoryService, DocumentService, TemplateService, FolderService, TagService
    from .mappers import (
        CategoryAggregate,
        CategoryNodeObject,
        DocumentAggregate,
        DocumentSectionAggregate,
        DocumentTableObject,
        DocumentSectionNodeObject,
        DocumentLinkAggregate,
        DocumentLinkTableObject,
        SectionCommentAggregate,
        SectionCommentTableObject,
        SectionRevisionNodeObject,
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
        SearchKeywordSections,
        SearchComposedSections,
        RemoveEmbedding,
        ImportMarkdownDocument,
        ExportDocumentMarkdown,
        AddDocumentLink,
        RemoveDocumentLink,
        ListDocumentLinks,
    )
except Exception as e:
    import os, sys
    if not os.getenv(SILENT_IMPORTS):
        print(f'Warning: Failed to import tiferet_kb modules: {e}', file=sys.stderr)

# *** version

__version__ = '1.0.0b4'
