"""tiferet_kb Asset Catalog Tests"""

# *** imports

# ** core
import ast
import importlib
import inspect
from pathlib import Path

# ** app
from tiferet.assets.core import (
    EN_US,
    create_app_service_dependency_data,
    create_default_app_session_data,
    create_default_error_data,
    create_default_feature_data,
)
from tiferet.events import DomainEvent

from ..app import KB_APP_SESSION_ID, KB_DEFAULT_APP_SESSIONS, KB_DEFAULT_SERVICES
from ..error import KB_DEFAULT_ERRORS, KB_INVALID_VISIBILITY_MESSAGE
from ..feature import KB_DEFAULT_FEATURES

# *** constants

# ** constant: visibility_message
VISIBILITY_MESSAGE = (
    'Invalid visibility: {visibility}. Must be public, private, or restricted'
)

# ** constant: error_rows
ERROR_ROWS = (
    ('KB_DOCUMENT_NOT_FOUND', 'Document Not Found', 'Document not found: {document_id}'),
    ('KB_DOCUMENT_ALREADY_EXISTS', 'Document Already Exists', 'Document with ID {id} already exists'),
    ('KB_DOCUMENT_LINK_ALREADY_EXISTS', 'Document Link Already Exists', 'Document link already exists: {id}'),
    ('KB_INVALID_DOCUMENT_LINK', 'Invalid Document Link', 'Invalid document link: {message}'),
    ('KB_DOCUMENT_SECTION_NOT_FOUND', 'Document Section Not Found', 'Document section not found: {section_id}'),
    ('KB_SECTION_REVISION_NOT_FOUND', 'Section Revision Not Found', 'Section revision not found: {number}'),
    ('KB_INVALID_DOCUMENT_STATUS', 'Invalid Document Status', 'Invalid document status: {status}. Must be draft, published, or archived'),
    ('KB_INVALID_VISIBILITY', 'Invalid Visibility', VISIBILITY_MESSAGE),
    ('KB_INVALID_DOCUMENT_ATTRIBUTE', 'Invalid Document Attribute', 'Invalid document attribute: {attribute}'),
    ('KB_INVALID_PROPERTY_NAME', 'Invalid Property Name', 'Invalid property name: {name}'),
    ('KB_INVALID_PROPERTY_TYPE', 'Invalid Property Type', 'Invalid property value type: {value_type}. Must be string, number, or boolean'),
    ('KB_INVALID_PROPERTY_VALUE', 'Invalid Property Value', 'Property value does not match value type {value_type}'),
    ('KB_INVALID_PROPERTY_FILTER', 'Invalid Property Filter', 'A property filter requires name, value, and value type'),
    ('KB_INVALID_SECTION_ATTRIBUTE', 'Invalid Section Attribute', 'Invalid section attribute: {attribute}'),
    ('KB_CATEGORY_NOT_FOUND', 'Category Not Found', 'Category not found: {category_id}'),
    ('KB_CATEGORY_ALREADY_EXISTS', 'Category Already Exists', 'Category with ID {id} already exists'),
    ('KB_CATEGORY_IN_USE', 'Category In Use', 'Category {id} is referenced by existing documents'),
    ('KB_INVALID_CATEGORY_ATTRIBUTE', 'Invalid Category Attribute', 'Invalid category attribute: {attribute}'),
    ('KB_TEMPLATE_NOT_FOUND', 'Template Not Found', 'Template not found: {template_id}'),
    ('KB_TEMPLATE_ALREADY_EXISTS', 'Template Already Exists', 'Template with ID {id} already exists'),
    ('KB_FOLDER_NOT_FOUND', 'Folder Not Found', 'Folder not found: {folder_id}'),
    ('KB_FOLDER_ALREADY_EXISTS', 'Folder Already Exists', 'Folder with ID {id} already exists'),
    ('KB_FOLDER_CIRCULAR_REFERENCE', 'Folder Circular Reference', 'Cannot move folder {folder_id} to create a circular reference'),
    ('KB_FOLDER_NOT_EMPTY', 'Folder Not Empty', 'Folder {folder_id} contains documents or subfolders'),
    ('KB_INVALID_CONTENT_TYPE', 'Invalid Content Type', 'Invalid content type: {content_type}. Must be text, markdown, code, table, or image'),
    ('KB_EMBEDDING_NOT_FOUND', 'Embedding Not Found', 'Embedding not found for section: {section_id}'),
    ('KB_EMBEDDING_DIMENSION_MISMATCH', 'Embedding Dimension Mismatch', 'Embedding dimension mismatch: expected {expected}, got {actual}'),
    ('KB_SECTION_NOT_EMBEDDED', 'Section Not Embedded', 'Section {section_id} has no embedding'),
    ('KB_TAG_NOT_FOUND', 'Tag Not Found', 'Tag not found: {tag_id}'),
    ('KB_TAG_ALREADY_EXISTS', 'Tag Already Exists', 'Tag with ID {id} already exists'),
    ('KB_TAG_IN_USE', 'Tag In Use', 'Tag {id} is carried by existing documents'),
    ('KB_INVALID_TAG_ATTRIBUTE', 'Invalid Tag Attribute', 'Invalid tag attribute: {attribute}'),
    ('KB_INVALID_SECTION_COMMENT', 'Invalid Section Comment', 'Invalid section comment: {field}'),
    ('KB_SECTION_COMMENT_ALREADY_EXISTS', 'Section Comment Already Exists', 'Section comment with ID {id} already exists'),
    ('KB_SECTION_COMMENT_HAS_REPLIES', 'Section Comment Has Replies', 'Section comment {id} still has replies'),
)

# ** constant: service_rows
SERVICE_ROWS = (
    ('category_service', 'tiferet_kb.repos.category', 'CategoryH5Repository'),
    ('document_service', 'tiferet_kb.repos.document', 'DocumentH5Repository'),
    ('template_service', 'tiferet_kb.repos.template', 'TemplateH5Repository'),
    ('folder_service', 'tiferet_kb.repos.folder', 'FolderH5Repository'),
    ('tag_service', 'tiferet_kb.repos.tag', 'TagH5Repository'),
    ('add_category_event', 'tiferet_kb.events.category', 'AddCategory'),
    ('get_category_event', 'tiferet_kb.events.category', 'GetCategory'),
    ('list_categories_event', 'tiferet_kb.events.category', 'ListCategories'),
    ('update_category_event', 'tiferet_kb.events.category', 'UpdateCategory'),
    ('remove_category_event', 'tiferet_kb.events.category', 'RemoveCategory'),
    ('add_section_comment_event', 'tiferet_kb.events.comment', 'AddSectionComment'),
    ('list_section_comments_event', 'tiferet_kb.events.comment', 'ListSectionComments'),
    ('remove_section_comment_event', 'tiferet_kb.events.comment', 'RemoveSectionComment'),
    ('add_document_event', 'tiferet_kb.events.document', 'AddDocument'),
    ('get_document_event', 'tiferet_kb.events.document', 'GetDocument'),
    ('list_documents_event', 'tiferet_kb.events.document', 'ListDocuments'),
    ('update_document_event', 'tiferet_kb.events.document', 'UpdateDocument'),
    ('set_document_visibility_event', 'tiferet_kb.events.document', 'SetDocumentVisibility'),
    ('remove_document_event', 'tiferet_kb.events.document', 'RemoveDocument'),
    ('add_document_section_event', 'tiferet_kb.events.document', 'AddDocumentSection'),
    ('update_document_section_event', 'tiferet_kb.events.document', 'UpdateDocumentSection'),
    ('list_document_section_revisions_event', 'tiferet_kb.events.document', 'ListDocumentSectionRevisions'),
    ('restore_document_section_revision_event', 'tiferet_kb.events.document', 'RestoreDocumentSectionRevision'),
    ('remove_document_section_event', 'tiferet_kb.events.document', 'RemoveDocumentSection'),
    ('reorder_document_sections_event', 'tiferet_kb.events.document', 'ReorderDocumentSections'),
    ('set_document_property_event', 'tiferet_kb.events.document', 'SetDocumentProperty'),
    ('remove_document_property_event', 'tiferet_kb.events.document', 'RemoveDocumentProperty'),
    ('add_document_link_event', 'tiferet_kb.events.document_link', 'AddDocumentLink'),
    ('remove_document_link_event', 'tiferet_kb.events.document_link', 'RemoveDocumentLink'),
    ('list_document_links_event', 'tiferet_kb.events.document_link', 'ListDocumentLinks'),
    ('add_template_event', 'tiferet_kb.events.template', 'AddTemplate'),
    ('get_template_event', 'tiferet_kb.events.template', 'GetTemplate'),
    ('list_templates_event', 'tiferet_kb.events.template', 'ListTemplates'),
    ('update_template_event', 'tiferet_kb.events.template', 'UpdateTemplate'),
    ('remove_template_event', 'tiferet_kb.events.template', 'RemoveTemplate'),
    ('apply_template_event', 'tiferet_kb.events.template', 'ApplyTemplate'),
    ('embed_document_sections_event', 'tiferet_kb.events.embedding', 'EmbedDocumentSections'),
    ('search_similar_sections_event', 'tiferet_kb.events.embedding', 'SearchSimilarSections'),
    ('remove_embedding_event', 'tiferet_kb.events.embedding', 'RemoveEmbedding'),
    ('search_keyword_sections_event', 'tiferet_kb.events.search', 'SearchKeywordSections'),
    ('search_composed_sections_event', 'tiferet_kb.events.search', 'SearchComposedSections'),
    ('add_folder_event', 'tiferet_kb.events.folder', 'AddFolder'),
    ('get_folder_event', 'tiferet_kb.events.folder', 'GetFolder'),
    ('set_folder_visibility_event', 'tiferet_kb.events.folder', 'SetFolderVisibility'),
    ('list_folder_contents_event', 'tiferet_kb.events.folder', 'ListFolderContents'),
    ('move_folder_event', 'tiferet_kb.events.folder', 'MoveFolder'),
    ('move_document_event', 'tiferet_kb.events.folder', 'MoveDocument'),
    ('remove_folder_event', 'tiferet_kb.events.folder', 'RemoveFolder'),
    ('import_markdown_document_event', 'tiferet_kb.events.markdown', 'ImportMarkdownDocument'),
    ('export_document_markdown_event', 'tiferet_kb.events.markdown', 'ExportDocumentMarkdown'),
    ('add_tag_event', 'tiferet_kb.events.tag', 'AddTag'),
    ('get_tag_event', 'tiferet_kb.events.tag', 'GetTag'),
    ('list_tags_event', 'tiferet_kb.events.tag', 'ListTags'),
    ('update_tag_event', 'tiferet_kb.events.tag', 'UpdateTag'),
    ('remove_tag_event', 'tiferet_kb.events.tag', 'RemoveTag'),
    ('tag_document_event', 'tiferet_kb.events.tag', 'TagDocument'),
    ('untag_document_event', 'tiferet_kb.events.tag', 'UntagDocument'),
    ('list_document_tags_event', 'tiferet_kb.events.tag', 'ListDocumentTags'),
)

# ** constant: feature_rows
FEATURE_ROWS = (
    ('category.add', 'Add Category', 'Create a new knowledge base category', 'Add category', 'add_category_event'),
    ('category.get', 'Get Category', 'Retrieve a category by ID', 'Get category', 'get_category_event'),
    ('category.list', 'List Categories', 'List all categories', 'List categories', 'list_categories_event'),
    ('category.update', 'Update Category', 'Update a category attribute', 'Update category', 'update_category_event'),
    ('category.remove', 'Remove Category', 'Remove a category', 'Remove category', 'remove_category_event'),
    ('comment.add', 'Add Section Comment', 'Add a plain-text note to a section', 'Add section comment', 'add_section_comment_event'),
    ('comment.list', 'List Section Comments', 'List comments on a section', 'List section comments', 'list_section_comments_event'),
    ('comment.remove', 'Remove Section Comment', 'Remove a section comment', 'Remove section comment', 'remove_section_comment_event'),
    ('document.add', 'Add Document', 'Create a new document', 'Add document', 'add_document_event'),
    ('document.get', 'Get Document', 'Retrieve a document with sections', 'Get document', 'get_document_event'),
    ('document.list', 'List Documents', 'List documents with optional filters', 'List documents', 'list_documents_event'),
    ('document.update', 'Update Document', 'Update a document attribute', 'Update document', 'update_document_event'),
    ('document.set_visibility', 'Set Document Visibility', 'Set visibility and owner on an existing document', 'Set document visibility', 'set_document_visibility_event'),
    ('document.remove', 'Remove Document', 'Remove a document and its sections', 'Remove document', 'remove_document_event'),
    ('section.add', 'Add Section', 'Add a section to a document', 'Add section', 'add_document_section_event'),
    ('section.update', 'Update Section', 'Update a section attribute', 'Update section', 'update_document_section_event'),
    ('section.list_revisions', 'List Section Revisions', "List a section's revisions newest first", 'List section revisions', 'list_document_section_revisions_event'),
    ('section.restore', 'Restore Section Revision', "Restore a section's paragraphs from a revision", 'Restore section revision', 'restore_document_section_revision_event'),
    ('section.remove', 'Remove Section', 'Remove a section from a document', 'Remove section', 'remove_document_section_event'),
    ('section.reorder', 'Reorder Sections', 'Reorder sections within a document', 'Reorder sections', 'reorder_document_sections_event'),
    ('document.set_property', 'Set Document Property', 'Set a named typed value on a document', 'Set document property', 'set_document_property_event'),
    ('document.remove_property', 'Remove Document Property', 'Remove a named value from a document', 'Remove document property', 'remove_document_property_event'),
    ('document_link.add', 'Add Document Link', 'Link one document to another in this file', 'Add document link', 'add_document_link_event'),
    ('document_link.remove', 'Remove Document Link', 'Remove a document link by id', 'Remove document link', 'remove_document_link_event'),
    ('document_link.list', 'List Document Links', 'List links for one document', 'List document links', 'list_document_links_event'),
    ('template.add', 'Add Template', 'Create a new template', 'Add template', 'add_template_event'),
    ('template.get', 'Get Template', 'Retrieve a template with sections', 'Get template', 'get_template_event'),
    ('template.list', 'List Templates', 'List templates', 'List templates', 'list_templates_event'),
    ('template.update', 'Update Template', 'Update a template attribute', 'Update template', 'update_template_event'),
    ('template.remove', 'Remove Template', 'Remove a template and its sections', 'Remove template', 'remove_template_event'),
    ('template.apply', 'Apply Template', 'Create a document from a template', 'Apply template', 'apply_template_event'),
    ('embedding.embed', 'Embed Document Sections', "Batch-store embedding vectors for a document's sections.", 'Embed document sections', 'embed_document_sections_event'),
    ('embedding.search_similar', 'Search Similar Sections', 'Search for document sections similar to a query embedding.', 'Search similar sections', 'search_similar_sections_event'),
    ('embedding.remove', 'Remove Embedding', "Remove a section's embedding vector.", 'Remove embedding', 'remove_embedding_event'),
    ('search.keyword', 'Search Keyword Sections', 'Rank sections by the words in their rendered bodies.', 'Search keyword sections', 'search_keyword_sections_event'),
    ('search.composed', 'Search Composed Sections', 'Merge keyword rank with embedding rank for one query.', 'Search composed sections', 'search_composed_sections_event'),
    ('folder.add', 'Add Folder', 'Create a new folder', 'Add folder', 'add_folder_event'),
    ('folder.get', 'Get Folder', 'Retrieve a folder by ID', 'Get folder', 'get_folder_event'),
    ('folder.set_visibility', 'Set Folder Visibility', 'Set visibility and owner on an existing folder', 'Set folder visibility', 'set_folder_visibility_event'),
    ('folder.contents', 'List Folder Contents', 'List child folders and documents', 'List folder contents', 'list_folder_contents_event'),
    ('folder.move', 'Move Folder', 'Move a folder to a new parent', 'Move folder', 'move_folder_event'),
    ('folder.move_document', 'Move Document', 'Move a document to a folder', 'Move document', 'move_document_event'),
    ('folder.remove', 'Remove Folder', 'Remove a folder and unfile its documents', 'Remove folder', 'remove_folder_event'),
    ('markdown.import', 'Import Markdown Document', 'Import a markdown string as a new document with sections.', 'Import markdown document', 'import_markdown_document_event'),
    ('markdown.export', 'Export Document Markdown', 'Export a document and its sections as a markdown string.', 'Export document markdown', 'export_document_markdown_event'),
    ('tag.add', 'Add Tag', 'Create a new knowledge base tag', 'Add tag', 'add_tag_event'),
    ('tag.get', 'Get Tag', 'Retrieve a tag by ID', 'Get tag', 'get_tag_event'),
    ('tag.list', 'List Tags', 'List all tags', 'List tags', 'list_tags_event'),
    ('tag.update', 'Update Tag', 'Update a tag attribute', 'Update tag', 'update_tag_event'),
    ('tag.remove', 'Remove Tag', 'Remove a tag that no document carries', 'Remove tag', 'remove_tag_event'),
    ('tag.tag_document', 'Tag Document', 'Record that a document carries a tag', 'Tag document', 'tag_document_event'),
    ('tag.untag_document', 'Untag Document', 'Remove a document-tag association', 'Untag document', 'untag_document_event'),
    ('tag.list_document_tags', 'List Document Tags', 'List the tags a document carries', 'List document tags', 'list_document_tags_event'),
)

# ** constant: multi_service_events
MULTI_SERVICE_EVENTS = (
    ('tiferet_kb.events.category', 'RemoveCategory', ('category_service', 'document_service')),
    ('tiferet_kb.events.document', 'ListDocuments', ('document_service', 'tag_service')),
    ('tiferet_kb.events.document', 'RemoveDocument', ('document_service', 'tag_service')),
    ('tiferet_kb.events.template', 'ApplyTemplate', ('template_service', 'document_service')),
    ('tiferet_kb.events.folder', 'ListFolderContents', ('folder_service', 'document_service')),
    ('tiferet_kb.events.folder', 'RemoveFolder', ('folder_service', 'document_service')),
    ('tiferet_kb.events.tag', 'TagDocument', ('document_service', 'tag_service')),
    ('tiferet_kb.events.tag', 'ListDocumentTags', ('document_service', 'tag_service')),
)

# ** constant: package_root_names
PACKAGE_ROOT_NAMES = (
    'Category',
    'Document',
    'DocumentSection',
    'SectionRevision',
    'DocumentLink',
    'SectionComment',
    'EmbeddingRecord',
    'TextSegment',
    'Paragraph',
    'Template',
    'TemplateSection',
    'Folder',
    'Tag',
    'CategoryService',
    'DocumentService',
    'TemplateService',
    'FolderService',
    'TagService',
    'CategoryAggregate',
    'CategoryNodeObject',
    'DocumentAggregate',
    'DocumentSectionAggregate',
    'DocumentTableObject',
    'DocumentSectionNodeObject',
    'DocumentLinkAggregate',
    'DocumentLinkTableObject',
    'SectionCommentAggregate',
    'SectionCommentTableObject',
    'SectionRevisionNodeObject',
    'HybridSegmentTableObject',
    'EmbeddingRecordAggregate',
    'TemplateAggregate',
    'TemplateSectionAggregate',
    'TemplateTableObject',
    'TemplateSectionTableObject',
    'FolderAggregate',
    'FolderNodeObject',
    'TagAggregate',
    'TagNodeObject',
    'EmbedDocumentSections',
    'SearchSimilarSections',
    'SearchKeywordSections',
    'SearchComposedSections',
    'RemoveEmbedding',
    'ImportMarkdownDocument',
    'ExportDocumentMarkdown',
    'AddDocumentLink',
    'RemoveDocumentLink',
    'ListDocumentLinks',
)

# *** functions

# ** function: init_parameters
def init_parameters(cls) -> tuple:
    '''
    Return constructor parameter names, excluding self.

    :param cls: The event class.
    :type cls: type
    :return: Parameter names in signature order.
    :rtype: tuple
    '''

    # Drop self. Inherited arguments stay in the signature.
    names = [
        name for name in inspect.signature(cls.__init__).parameters
        if name != 'self'
    ]
    return tuple(names)

# *** tests

# ** test: errors_match_the_transcribed_rows
def test_errors_match_the_transcribed_rows():
    '''The error catalog has 35 rows, in order, with no embedded id.'''

    assert list(KB_DEFAULT_ERRORS) == [row[0] for row in ERROR_ROWS]
    assert KB_INVALID_VISIBILITY_MESSAGE == VISIBILITY_MESSAGE
    for code, name, text in ERROR_ROWS:
        value = KB_DEFAULT_ERRORS[code]
        assert 'id' not in value
        assert value == create_default_error_data(name, [(EN_US, text)])
    visibility = KB_DEFAULT_ERRORS['KB_INVALID_VISIBILITY']
    assert visibility['message'][0]['text'] == KB_INVALID_VISIBILITY_MESSAGE

# ** test: services_match_the_transcribed_rows
def test_services_match_the_transcribed_rows():
    '''The service catalog has 58 rows and no path, mode, or embedded id.'''

    assert list(KB_DEFAULT_SERVICES) == [row[0] for row in SERVICE_ROWS]
    for service_id, module_path, class_name in SERVICE_ROWS:
        value = KB_DEFAULT_SERVICES[service_id]
        assert value == create_app_service_dependency_data(module_path, class_name)
        assert value['parameters'] == {}
        assert 'id' not in value
        assert 'service_id' not in value
        assert 'h5_file' not in value
        assert 'mode' not in value
        assert 'h5_file' not in str(value)
        module = importlib.import_module(module_path)
        assert hasattr(module, class_name)

# ** test: features_match_the_transcribed_rows
def test_features_match_the_transcribed_rows():
    '''The feature catalog has 53 rows and one unflagged event step each.'''

    assert list(KB_DEFAULT_FEATURES) == [row[0] for row in FEATURE_ROWS]
    for feature_id, name, description, step_name, service_id in FEATURE_ROWS:
        group_id, feature_key = feature_id.split('.', 1)
        value = KB_DEFAULT_FEATURES[feature_id]
        assert value == create_default_feature_data(
            name,
            group_id,
            feature_key,
            [{'service_id': service_id, 'name': step_name}],
            description=description,
        )
        assert 'id' not in value
        assert 'params_schema' not in value
        assert 'commands' not in value
        assert 'attribute_id' not in value
        assert value['steps'][0]['service_id'] == service_id

# ** test: session_is_the_one_kb_row
def test_session_is_the_one_kb_row():
    '''The session catalog has one key and does not embed id or constants.'''

    assert list(KB_DEFAULT_APP_SESSIONS) == [KB_APP_SESSION_ID]
    assert KB_APP_SESSION_ID == 'kb'
    value = KB_DEFAULT_APP_SESSIONS['kb']
    assert value == create_default_app_session_data(
        'Knowledge Base',
        description='One file holding documents, structure, and retrieval.',
    )
    assert 'id' not in value
    assert 'constants' not in value
    assert 'services' not in value

# ** test: catalog_modules_do_not_name_yaml_or_the_retired_dict
def test_catalog_modules_do_not_name_yaml_or_the_retired_dict():
    '''The new modules do not cite YAML, and DEFAULT_ERRORS is gone.'''

    assets = Path(__file__).resolve().parents[1]
    root = assets.parents[1]
    for name in ('error.py', 'app.py', 'feature.py'):
        source = (assets / name).read_text()
        tree = ast.parse(source)
        names = {
            node.id for node in ast.walk(tree)
            if isinstance(node, ast.Name)
        }
        assert 'DEFAULT_ERRORS' not in names
        for filename in ('app.yml', 'container.yml', 'feature.yml', 'error.yml'):
            assert filename not in source
    assert not (assets / 'errors.py').exists()
    for filename in ('app.yml', 'container.yml', 'feature.yml', 'error.yml'):
        assert not (root / 'app' / 'configs' / filename).exists()

# ** test: multi_service_constructors_keep_both_arguments
def test_multi_service_constructors_keep_both_arguments():
    '''The eight multi-service events still take both listed services.'''

    for module_path, class_name, expected in MULTI_SERVICE_EVENTS:
        cls = getattr(importlib.import_module(module_path), class_name)
        assert init_parameters(cls) == expected

    events = Path(__file__).resolve().parents[2] / 'events'
    for path in events.glob('*.py'):
        if path.name == '__init__.py':
            continue
        module = importlib.import_module(f'tiferet_kb.events.{path.stem}')
        for cls in vars(module).values():
            if not inspect.isclass(cls) or not issubclass(cls, DomainEvent):
                continue
            if cls.__module__ != module.__name__:
                continue
            names = init_parameters(cls)
            assert 'h5_file' not in names
            assert 'mode' not in names

# ** test: package_root_exports_bind
def test_package_root_exports_bind():
    '''A successful import binds the package-root names. The try must not hide a miss.'''

    import tiferet_kb
    from tiferet_kb import assets

    missing = [name for name in PACKAGE_ROOT_NAMES if not hasattr(tiferet_kb, name)]
    assert missing == []
    assert not hasattr(tiferet_kb, 'DEFAULT_ERRORS')
    assert not hasattr(assets, 'DEFAULT_ERRORS')
    assert not hasattr(tiferet_kb, 'build_cache')
    assert not hasattr(assets, 'KB_DEFAULT_CONSTANTS')
