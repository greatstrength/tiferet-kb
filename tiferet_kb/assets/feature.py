"""tiferet_kb Feature Catalog"""

# *** imports

# ** app
from tiferet.assets.core import create_default_feature_data

# *** constants (ids)

# ** constant: category_add_id
CATEGORY_ADD_ID = 'category.add'

# ** constant: category_get_id
CATEGORY_GET_ID = 'category.get'

# ** constant: category_list_id
CATEGORY_LIST_ID = 'category.list'

# ** constant: category_update_id
CATEGORY_UPDATE_ID = 'category.update'

# ** constant: category_remove_id
CATEGORY_REMOVE_ID = 'category.remove'

# ** constant: comment_add_id
COMMENT_ADD_ID = 'comment.add'

# ** constant: comment_list_id
COMMENT_LIST_ID = 'comment.list'

# ** constant: comment_remove_id
COMMENT_REMOVE_ID = 'comment.remove'

# ** constant: document_add_id
DOCUMENT_ADD_ID = 'document.add'

# ** constant: document_get_id
DOCUMENT_GET_ID = 'document.get'

# ** constant: document_list_id
DOCUMENT_LIST_ID = 'document.list'

# ** constant: document_update_id
DOCUMENT_UPDATE_ID = 'document.update'

# ** constant: document_set_visibility_id
DOCUMENT_SET_VISIBILITY_ID = 'document.set_visibility'

# ** constant: document_remove_id
DOCUMENT_REMOVE_ID = 'document.remove'

# ** constant: section_add_id
SECTION_ADD_ID = 'section.add'

# ** constant: section_update_id
SECTION_UPDATE_ID = 'section.update'

# ** constant: section_list_revisions_id
SECTION_LIST_REVISIONS_ID = 'section.list_revisions'

# ** constant: section_restore_id
SECTION_RESTORE_ID = 'section.restore'

# ** constant: section_remove_id
SECTION_REMOVE_ID = 'section.remove'

# ** constant: section_reorder_id
SECTION_REORDER_ID = 'section.reorder'

# ** constant: document_set_property_id
DOCUMENT_SET_PROPERTY_ID = 'document.set_property'

# ** constant: document_remove_property_id
DOCUMENT_REMOVE_PROPERTY_ID = 'document.remove_property'

# ** constant: document_link_add_id
DOCUMENT_LINK_ADD_ID = 'document_link.add'

# ** constant: document_link_remove_id
DOCUMENT_LINK_REMOVE_ID = 'document_link.remove'

# ** constant: document_link_list_id
DOCUMENT_LINK_LIST_ID = 'document_link.list'

# ** constant: template_add_id
TEMPLATE_ADD_ID = 'template.add'

# ** constant: template_get_id
TEMPLATE_GET_ID = 'template.get'

# ** constant: template_list_id
TEMPLATE_LIST_ID = 'template.list'

# ** constant: template_update_id
TEMPLATE_UPDATE_ID = 'template.update'

# ** constant: template_remove_id
TEMPLATE_REMOVE_ID = 'template.remove'

# ** constant: template_apply_id
TEMPLATE_APPLY_ID = 'template.apply'

# ** constant: embedding_embed_id
EMBEDDING_EMBED_ID = 'embedding.embed'

# ** constant: embedding_search_similar_id
EMBEDDING_SEARCH_SIMILAR_ID = 'embedding.search_similar'

# ** constant: embedding_remove_id
EMBEDDING_REMOVE_ID = 'embedding.remove'

# ** constant: search_keyword_id
SEARCH_KEYWORD_ID = 'search.keyword'

# ** constant: search_composed_id
SEARCH_COMPOSED_ID = 'search.composed'

# ** constant: folder_add_id
FOLDER_ADD_ID = 'folder.add'

# ** constant: folder_get_id
FOLDER_GET_ID = 'folder.get'

# ** constant: folder_set_visibility_id
FOLDER_SET_VISIBILITY_ID = 'folder.set_visibility'

# ** constant: folder_contents_id
FOLDER_CONTENTS_ID = 'folder.contents'

# ** constant: folder_move_id
FOLDER_MOVE_ID = 'folder.move'

# ** constant: folder_move_document_id
FOLDER_MOVE_DOCUMENT_ID = 'folder.move_document'

# ** constant: folder_remove_id
FOLDER_REMOVE_ID = 'folder.remove'

# ** constant: markdown_import_id
MARKDOWN_IMPORT_ID = 'markdown.import'

# ** constant: markdown_export_id
MARKDOWN_EXPORT_ID = 'markdown.export'

# ** constant: tag_add_id
TAG_ADD_ID = 'tag.add'

# ** constant: tag_get_id
TAG_GET_ID = 'tag.get'

# ** constant: tag_list_id
TAG_LIST_ID = 'tag.list'

# ** constant: tag_update_id
TAG_UPDATE_ID = 'tag.update'

# ** constant: tag_remove_id
TAG_REMOVE_ID = 'tag.remove'

# ** constant: tag_tag_document_id
TAG_TAG_DOCUMENT_ID = 'tag.tag_document'

# ** constant: tag_untag_document_id
TAG_UNTAG_DOCUMENT_ID = 'tag.untag_document'

# ** constant: tag_list_document_tags_id
TAG_LIST_DOCUMENT_TAGS_ID = 'tag.list_document_tags'

# *** constants (models)

# ** constant: category_add_data
CATEGORY_ADD_DATA = create_default_feature_data(
    'Add Category',
    'category',
    'add',
    [
        {
            'service_id': 'add_category_event',
            'name': 'Add category',
        },
    ],
    description='Create a new knowledge base category',
)

# ** constant: category_get_data
CATEGORY_GET_DATA = create_default_feature_data(
    'Get Category',
    'category',
    'get',
    [
        {
            'service_id': 'get_category_event',
            'name': 'Get category',
        },
    ],
    description='Retrieve a category by ID',
)

# ** constant: category_list_data
CATEGORY_LIST_DATA = create_default_feature_data(
    'List Categories',
    'category',
    'list',
    [
        {
            'service_id': 'list_categories_event',
            'name': 'List categories',
        },
    ],
    description='List all categories',
)

# ** constant: category_update_data
CATEGORY_UPDATE_DATA = create_default_feature_data(
    'Update Category',
    'category',
    'update',
    [
        {
            'service_id': 'update_category_event',
            'name': 'Update category',
        },
    ],
    description='Update a category attribute',
)

# ** constant: category_remove_data
CATEGORY_REMOVE_DATA = create_default_feature_data(
    'Remove Category',
    'category',
    'remove',
    [
        {
            'service_id': 'remove_category_event',
            'name': 'Remove category',
        },
    ],
    description='Remove a category',
)

# ** constant: comment_add_data
COMMENT_ADD_DATA = create_default_feature_data(
    'Add Section Comment',
    'comment',
    'add',
    [
        {
            'service_id': 'add_section_comment_event',
            'name': 'Add section comment',
        },
    ],
    description='Add a plain-text note to a section',
)

# ** constant: comment_list_data
COMMENT_LIST_DATA = create_default_feature_data(
    'List Section Comments',
    'comment',
    'list',
    [
        {
            'service_id': 'list_section_comments_event',
            'name': 'List section comments',
        },
    ],
    description='List comments on a section',
)

# ** constant: comment_remove_data
COMMENT_REMOVE_DATA = create_default_feature_data(
    'Remove Section Comment',
    'comment',
    'remove',
    [
        {
            'service_id': 'remove_section_comment_event',
            'name': 'Remove section comment',
        },
    ],
    description='Remove a section comment',
)

# ** constant: document_add_data
DOCUMENT_ADD_DATA = create_default_feature_data(
    'Add Document',
    'document',
    'add',
    [
        {
            'service_id': 'add_document_event',
            'name': 'Add document',
        },
    ],
    description='Create a new document',
)

# ** constant: document_get_data
DOCUMENT_GET_DATA = create_default_feature_data(
    'Get Document',
    'document',
    'get',
    [
        {
            'service_id': 'get_document_event',
            'name': 'Get document',
        },
    ],
    description='Retrieve a document with sections',
)

# ** constant: document_list_data
DOCUMENT_LIST_DATA = create_default_feature_data(
    'List Documents',
    'document',
    'list',
    [
        {
            'service_id': 'list_documents_event',
            'name': 'List documents',
        },
    ],
    description='List documents with optional filters',
)

# ** constant: document_update_data
DOCUMENT_UPDATE_DATA = create_default_feature_data(
    'Update Document',
    'document',
    'update',
    [
        {
            'service_id': 'update_document_event',
            'name': 'Update document',
        },
    ],
    description='Update a document attribute',
)

# ** constant: document_set_visibility_data
DOCUMENT_SET_VISIBILITY_DATA = create_default_feature_data(
    'Set Document Visibility',
    'document',
    'set_visibility',
    [
        {
            'service_id': 'set_document_visibility_event',
            'name': 'Set document visibility',
        },
    ],
    description='Set visibility and owner on an existing document',
)

# ** constant: document_remove_data
DOCUMENT_REMOVE_DATA = create_default_feature_data(
    'Remove Document',
    'document',
    'remove',
    [
        {
            'service_id': 'remove_document_event',
            'name': 'Remove document',
        },
    ],
    description='Remove a document and its sections',
)

# ** constant: section_add_data
SECTION_ADD_DATA = create_default_feature_data(
    'Add Section',
    'section',
    'add',
    [
        {
            'service_id': 'add_document_section_event',
            'name': 'Add section',
        },
    ],
    description='Add a section to a document',
)

# ** constant: section_update_data
SECTION_UPDATE_DATA = create_default_feature_data(
    'Update Section',
    'section',
    'update',
    [
        {
            'service_id': 'update_document_section_event',
            'name': 'Update section',
        },
    ],
    description='Update a section attribute',
)

# ** constant: section_list_revisions_data
SECTION_LIST_REVISIONS_DATA = create_default_feature_data(
    'List Section Revisions',
    'section',
    'list_revisions',
    [
        {
            'service_id': 'list_document_section_revisions_event',
            'name': 'List section revisions',
        },
    ],
    description='List a section\'s revisions newest first',
)

# ** constant: section_restore_data
SECTION_RESTORE_DATA = create_default_feature_data(
    'Restore Section Revision',
    'section',
    'restore',
    [
        {
            'service_id': 'restore_document_section_revision_event',
            'name': 'Restore section revision',
        },
    ],
    description='Restore a section\'s paragraphs from a revision',
)

# ** constant: section_remove_data
SECTION_REMOVE_DATA = create_default_feature_data(
    'Remove Section',
    'section',
    'remove',
    [
        {
            'service_id': 'remove_document_section_event',
            'name': 'Remove section',
        },
    ],
    description='Remove a section from a document',
)

# ** constant: section_reorder_data
SECTION_REORDER_DATA = create_default_feature_data(
    'Reorder Sections',
    'section',
    'reorder',
    [
        {
            'service_id': 'reorder_document_sections_event',
            'name': 'Reorder sections',
        },
    ],
    description='Reorder sections within a document',
)

# ** constant: document_set_property_data
DOCUMENT_SET_PROPERTY_DATA = create_default_feature_data(
    'Set Document Property',
    'document',
    'set_property',
    [
        {
            'service_id': 'set_document_property_event',
            'name': 'Set document property',
        },
    ],
    description='Set a named typed value on a document',
)

# ** constant: document_remove_property_data
DOCUMENT_REMOVE_PROPERTY_DATA = create_default_feature_data(
    'Remove Document Property',
    'document',
    'remove_property',
    [
        {
            'service_id': 'remove_document_property_event',
            'name': 'Remove document property',
        },
    ],
    description='Remove a named value from a document',
)

# ** constant: document_link_add_data
DOCUMENT_LINK_ADD_DATA = create_default_feature_data(
    'Add Document Link',
    'document_link',
    'add',
    [
        {
            'service_id': 'add_document_link_event',
            'name': 'Add document link',
        },
    ],
    description='Link one document to another in this file',
)

# ** constant: document_link_remove_data
DOCUMENT_LINK_REMOVE_DATA = create_default_feature_data(
    'Remove Document Link',
    'document_link',
    'remove',
    [
        {
            'service_id': 'remove_document_link_event',
            'name': 'Remove document link',
        },
    ],
    description='Remove a document link by id',
)

# ** constant: document_link_list_data
DOCUMENT_LINK_LIST_DATA = create_default_feature_data(
    'List Document Links',
    'document_link',
    'list',
    [
        {
            'service_id': 'list_document_links_event',
            'name': 'List document links',
        },
    ],
    description='List links for one document',
)

# ** constant: template_add_data
TEMPLATE_ADD_DATA = create_default_feature_data(
    'Add Template',
    'template',
    'add',
    [
        {
            'service_id': 'add_template_event',
            'name': 'Add template',
        },
    ],
    description='Create a new template',
)

# ** constant: template_get_data
TEMPLATE_GET_DATA = create_default_feature_data(
    'Get Template',
    'template',
    'get',
    [
        {
            'service_id': 'get_template_event',
            'name': 'Get template',
        },
    ],
    description='Retrieve a template with sections',
)

# ** constant: template_list_data
TEMPLATE_LIST_DATA = create_default_feature_data(
    'List Templates',
    'template',
    'list',
    [
        {
            'service_id': 'list_templates_event',
            'name': 'List templates',
        },
    ],
    description='List templates',
)

# ** constant: template_update_data
TEMPLATE_UPDATE_DATA = create_default_feature_data(
    'Update Template',
    'template',
    'update',
    [
        {
            'service_id': 'update_template_event',
            'name': 'Update template',
        },
    ],
    description='Update a template attribute',
)

# ** constant: template_remove_data
TEMPLATE_REMOVE_DATA = create_default_feature_data(
    'Remove Template',
    'template',
    'remove',
    [
        {
            'service_id': 'remove_template_event',
            'name': 'Remove template',
        },
    ],
    description='Remove a template and its sections',
)

# ** constant: template_apply_data
TEMPLATE_APPLY_DATA = create_default_feature_data(
    'Apply Template',
    'template',
    'apply',
    [
        {
            'service_id': 'apply_template_event',
            'name': 'Apply template',
        },
    ],
    description='Create a document from a template',
)

# ** constant: embedding_embed_data
EMBEDDING_EMBED_DATA = create_default_feature_data(
    'Embed Document Sections',
    'embedding',
    'embed',
    [
        {
            'service_id': 'embed_document_sections_event',
            'name': 'Embed document sections',
        },
    ],
    description='Batch-store embedding vectors for a document\'s sections.',
)

# ** constant: embedding_search_similar_data
EMBEDDING_SEARCH_SIMILAR_DATA = create_default_feature_data(
    'Search Similar Sections',
    'embedding',
    'search_similar',
    [
        {
            'service_id': 'search_similar_sections_event',
            'name': 'Search similar sections',
        },
    ],
    description='Search for document sections similar to a query embedding.',
)

# ** constant: embedding_remove_data
EMBEDDING_REMOVE_DATA = create_default_feature_data(
    'Remove Embedding',
    'embedding',
    'remove',
    [
        {
            'service_id': 'remove_embedding_event',
            'name': 'Remove embedding',
        },
    ],
    description='Remove a section\'s embedding vector.',
)

# ** constant: search_keyword_data
SEARCH_KEYWORD_DATA = create_default_feature_data(
    'Search Keyword Sections',
    'search',
    'keyword',
    [
        {
            'service_id': 'search_keyword_sections_event',
            'name': 'Search keyword sections',
        },
    ],
    description='Rank sections by the words in their rendered bodies.',
)

# ** constant: search_composed_data
SEARCH_COMPOSED_DATA = create_default_feature_data(
    'Search Composed Sections',
    'search',
    'composed',
    [
        {
            'service_id': 'search_composed_sections_event',
            'name': 'Search composed sections',
        },
    ],
    description='Merge keyword rank with embedding rank for one query.',
)

# ** constant: folder_add_data
FOLDER_ADD_DATA = create_default_feature_data(
    'Add Folder',
    'folder',
    'add',
    [
        {
            'service_id': 'add_folder_event',
            'name': 'Add folder',
        },
    ],
    description='Create a new folder',
)

# ** constant: folder_get_data
FOLDER_GET_DATA = create_default_feature_data(
    'Get Folder',
    'folder',
    'get',
    [
        {
            'service_id': 'get_folder_event',
            'name': 'Get folder',
        },
    ],
    description='Retrieve a folder by ID',
)

# ** constant: folder_set_visibility_data
FOLDER_SET_VISIBILITY_DATA = create_default_feature_data(
    'Set Folder Visibility',
    'folder',
    'set_visibility',
    [
        {
            'service_id': 'set_folder_visibility_event',
            'name': 'Set folder visibility',
        },
    ],
    description='Set visibility and owner on an existing folder',
)

# ** constant: folder_contents_data
FOLDER_CONTENTS_DATA = create_default_feature_data(
    'List Folder Contents',
    'folder',
    'contents',
    [
        {
            'service_id': 'list_folder_contents_event',
            'name': 'List folder contents',
        },
    ],
    description='List child folders and documents',
)

# ** constant: folder_move_data
FOLDER_MOVE_DATA = create_default_feature_data(
    'Move Folder',
    'folder',
    'move',
    [
        {
            'service_id': 'move_folder_event',
            'name': 'Move folder',
        },
    ],
    description='Move a folder to a new parent',
)

# ** constant: folder_move_document_data
FOLDER_MOVE_DOCUMENT_DATA = create_default_feature_data(
    'Move Document',
    'folder',
    'move_document',
    [
        {
            'service_id': 'move_document_event',
            'name': 'Move document',
        },
    ],
    description='Move a document to a folder',
)

# ** constant: folder_remove_data
FOLDER_REMOVE_DATA = create_default_feature_data(
    'Remove Folder',
    'folder',
    'remove',
    [
        {
            'service_id': 'remove_folder_event',
            'name': 'Remove folder',
        },
    ],
    description='Remove a folder and unfile its documents',
)

# ** constant: markdown_import_data
MARKDOWN_IMPORT_DATA = create_default_feature_data(
    'Import Markdown Document',
    'markdown',
    'import',
    [
        {
            'service_id': 'import_markdown_document_event',
            'name': 'Import markdown document',
        },
    ],
    description='Import a markdown string as a new document with sections.',
)

# ** constant: markdown_export_data
MARKDOWN_EXPORT_DATA = create_default_feature_data(
    'Export Document Markdown',
    'markdown',
    'export',
    [
        {
            'service_id': 'export_document_markdown_event',
            'name': 'Export document markdown',
        },
    ],
    description='Export a document and its sections as a markdown string.',
)

# ** constant: tag_add_data
TAG_ADD_DATA = create_default_feature_data(
    'Add Tag',
    'tag',
    'add',
    [
        {
            'service_id': 'add_tag_event',
            'name': 'Add tag',
        },
    ],
    description='Create a new knowledge base tag',
)

# ** constant: tag_get_data
TAG_GET_DATA = create_default_feature_data(
    'Get Tag',
    'tag',
    'get',
    [
        {
            'service_id': 'get_tag_event',
            'name': 'Get tag',
        },
    ],
    description='Retrieve a tag by ID',
)

# ** constant: tag_list_data
TAG_LIST_DATA = create_default_feature_data(
    'List Tags',
    'tag',
    'list',
    [
        {
            'service_id': 'list_tags_event',
            'name': 'List tags',
        },
    ],
    description='List all tags',
)

# ** constant: tag_update_data
TAG_UPDATE_DATA = create_default_feature_data(
    'Update Tag',
    'tag',
    'update',
    [
        {
            'service_id': 'update_tag_event',
            'name': 'Update tag',
        },
    ],
    description='Update a tag attribute',
)

# ** constant: tag_remove_data
TAG_REMOVE_DATA = create_default_feature_data(
    'Remove Tag',
    'tag',
    'remove',
    [
        {
            'service_id': 'remove_tag_event',
            'name': 'Remove tag',
        },
    ],
    description='Remove a tag that no document carries',
)

# ** constant: tag_tag_document_data
TAG_TAG_DOCUMENT_DATA = create_default_feature_data(
    'Tag Document',
    'tag',
    'tag_document',
    [
        {
            'service_id': 'tag_document_event',
            'name': 'Tag document',
        },
    ],
    description='Record that a document carries a tag',
)

# ** constant: tag_untag_document_data
TAG_UNTAG_DOCUMENT_DATA = create_default_feature_data(
    'Untag Document',
    'tag',
    'untag_document',
    [
        {
            'service_id': 'untag_document_event',
            'name': 'Untag document',
        },
    ],
    description='Remove a document-tag association',
)

# ** constant: tag_list_document_tags_data
TAG_LIST_DOCUMENT_TAGS_DATA = create_default_feature_data(
    'List Document Tags',
    'tag',
    'list_document_tags',
    [
        {
            'service_id': 'list_document_tags_event',
            'name': 'List document tags',
        },
    ],
    description='List the tags a document carries',
)

# *** constants (groups)

# ** constant: kb_default_features
KB_DEFAULT_FEATURES = {
    CATEGORY_ADD_ID: CATEGORY_ADD_DATA,
    CATEGORY_GET_ID: CATEGORY_GET_DATA,
    CATEGORY_LIST_ID: CATEGORY_LIST_DATA,
    CATEGORY_UPDATE_ID: CATEGORY_UPDATE_DATA,
    CATEGORY_REMOVE_ID: CATEGORY_REMOVE_DATA,
    COMMENT_ADD_ID: COMMENT_ADD_DATA,
    COMMENT_LIST_ID: COMMENT_LIST_DATA,
    COMMENT_REMOVE_ID: COMMENT_REMOVE_DATA,
    DOCUMENT_ADD_ID: DOCUMENT_ADD_DATA,
    DOCUMENT_GET_ID: DOCUMENT_GET_DATA,
    DOCUMENT_LIST_ID: DOCUMENT_LIST_DATA,
    DOCUMENT_UPDATE_ID: DOCUMENT_UPDATE_DATA,
    DOCUMENT_SET_VISIBILITY_ID: DOCUMENT_SET_VISIBILITY_DATA,
    DOCUMENT_REMOVE_ID: DOCUMENT_REMOVE_DATA,
    SECTION_ADD_ID: SECTION_ADD_DATA,
    SECTION_UPDATE_ID: SECTION_UPDATE_DATA,
    SECTION_LIST_REVISIONS_ID: SECTION_LIST_REVISIONS_DATA,
    SECTION_RESTORE_ID: SECTION_RESTORE_DATA,
    SECTION_REMOVE_ID: SECTION_REMOVE_DATA,
    SECTION_REORDER_ID: SECTION_REORDER_DATA,
    DOCUMENT_SET_PROPERTY_ID: DOCUMENT_SET_PROPERTY_DATA,
    DOCUMENT_REMOVE_PROPERTY_ID: DOCUMENT_REMOVE_PROPERTY_DATA,
    DOCUMENT_LINK_ADD_ID: DOCUMENT_LINK_ADD_DATA,
    DOCUMENT_LINK_REMOVE_ID: DOCUMENT_LINK_REMOVE_DATA,
    DOCUMENT_LINK_LIST_ID: DOCUMENT_LINK_LIST_DATA,
    TEMPLATE_ADD_ID: TEMPLATE_ADD_DATA,
    TEMPLATE_GET_ID: TEMPLATE_GET_DATA,
    TEMPLATE_LIST_ID: TEMPLATE_LIST_DATA,
    TEMPLATE_UPDATE_ID: TEMPLATE_UPDATE_DATA,
    TEMPLATE_REMOVE_ID: TEMPLATE_REMOVE_DATA,
    TEMPLATE_APPLY_ID: TEMPLATE_APPLY_DATA,
    EMBEDDING_EMBED_ID: EMBEDDING_EMBED_DATA,
    EMBEDDING_SEARCH_SIMILAR_ID: EMBEDDING_SEARCH_SIMILAR_DATA,
    EMBEDDING_REMOVE_ID: EMBEDDING_REMOVE_DATA,
    SEARCH_KEYWORD_ID: SEARCH_KEYWORD_DATA,
    SEARCH_COMPOSED_ID: SEARCH_COMPOSED_DATA,
    FOLDER_ADD_ID: FOLDER_ADD_DATA,
    FOLDER_GET_ID: FOLDER_GET_DATA,
    FOLDER_SET_VISIBILITY_ID: FOLDER_SET_VISIBILITY_DATA,
    FOLDER_CONTENTS_ID: FOLDER_CONTENTS_DATA,
    FOLDER_MOVE_ID: FOLDER_MOVE_DATA,
    FOLDER_MOVE_DOCUMENT_ID: FOLDER_MOVE_DOCUMENT_DATA,
    FOLDER_REMOVE_ID: FOLDER_REMOVE_DATA,
    MARKDOWN_IMPORT_ID: MARKDOWN_IMPORT_DATA,
    MARKDOWN_EXPORT_ID: MARKDOWN_EXPORT_DATA,
    TAG_ADD_ID: TAG_ADD_DATA,
    TAG_GET_ID: TAG_GET_DATA,
    TAG_LIST_ID: TAG_LIST_DATA,
    TAG_UPDATE_ID: TAG_UPDATE_DATA,
    TAG_REMOVE_ID: TAG_REMOVE_DATA,
    TAG_TAG_DOCUMENT_ID: TAG_TAG_DOCUMENT_DATA,
    TAG_UNTAG_DOCUMENT_ID: TAG_UNTAG_DOCUMENT_DATA,
    TAG_LIST_DOCUMENT_TAGS_ID: TAG_LIST_DOCUMENT_TAGS_DATA,
}
