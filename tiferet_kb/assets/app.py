"""tiferet_kb App Catalog"""

# *** imports

# ** app
from tiferet.assets.core import (
    create_app_service_dependency_data,
    create_default_app_session_data,
)

# *** constants (ids)

# ** constant: category_service_id
CATEGORY_SERVICE_ID = 'category_service'

# ** constant: document_service_id
DOCUMENT_SERVICE_ID = 'document_service'

# ** constant: template_service_id
TEMPLATE_SERVICE_ID = 'template_service'

# ** constant: folder_service_id
FOLDER_SERVICE_ID = 'folder_service'

# ** constant: tag_service_id
TAG_SERVICE_ID = 'tag_service'

# ** constant: add_category_event_id
ADD_CATEGORY_EVENT_ID = 'add_category_event'

# ** constant: get_category_event_id
GET_CATEGORY_EVENT_ID = 'get_category_event'

# ** constant: list_categories_event_id
LIST_CATEGORIES_EVENT_ID = 'list_categories_event'

# ** constant: update_category_event_id
UPDATE_CATEGORY_EVENT_ID = 'update_category_event'

# ** constant: remove_category_event_id
REMOVE_CATEGORY_EVENT_ID = 'remove_category_event'

# ** constant: add_section_comment_event_id
ADD_SECTION_COMMENT_EVENT_ID = 'add_section_comment_event'

# ** constant: list_section_comments_event_id
LIST_SECTION_COMMENTS_EVENT_ID = 'list_section_comments_event'

# ** constant: remove_section_comment_event_id
REMOVE_SECTION_COMMENT_EVENT_ID = 'remove_section_comment_event'

# ** constant: add_document_event_id
ADD_DOCUMENT_EVENT_ID = 'add_document_event'

# ** constant: get_document_event_id
GET_DOCUMENT_EVENT_ID = 'get_document_event'

# ** constant: list_documents_event_id
LIST_DOCUMENTS_EVENT_ID = 'list_documents_event'

# ** constant: update_document_event_id
UPDATE_DOCUMENT_EVENT_ID = 'update_document_event'

# ** constant: set_document_visibility_event_id
SET_DOCUMENT_VISIBILITY_EVENT_ID = 'set_document_visibility_event'

# ** constant: remove_document_event_id
REMOVE_DOCUMENT_EVENT_ID = 'remove_document_event'

# ** constant: add_document_section_event_id
ADD_DOCUMENT_SECTION_EVENT_ID = 'add_document_section_event'

# ** constant: update_document_section_event_id
UPDATE_DOCUMENT_SECTION_EVENT_ID = 'update_document_section_event'

# ** constant: list_document_section_revisions_event_id
LIST_DOCUMENT_SECTION_REVISIONS_EVENT_ID = 'list_document_section_revisions_event'

# ** constant: restore_document_section_revision_event_id
RESTORE_DOCUMENT_SECTION_REVISION_EVENT_ID = 'restore_document_section_revision_event'

# ** constant: remove_document_section_event_id
REMOVE_DOCUMENT_SECTION_EVENT_ID = 'remove_document_section_event'

# ** constant: reorder_document_sections_event_id
REORDER_DOCUMENT_SECTIONS_EVENT_ID = 'reorder_document_sections_event'

# ** constant: set_document_property_event_id
SET_DOCUMENT_PROPERTY_EVENT_ID = 'set_document_property_event'

# ** constant: remove_document_property_event_id
REMOVE_DOCUMENT_PROPERTY_EVENT_ID = 'remove_document_property_event'

# ** constant: add_document_link_event_id
ADD_DOCUMENT_LINK_EVENT_ID = 'add_document_link_event'

# ** constant: remove_document_link_event_id
REMOVE_DOCUMENT_LINK_EVENT_ID = 'remove_document_link_event'

# ** constant: list_document_links_event_id
LIST_DOCUMENT_LINKS_EVENT_ID = 'list_document_links_event'

# ** constant: add_template_event_id
ADD_TEMPLATE_EVENT_ID = 'add_template_event'

# ** constant: get_template_event_id
GET_TEMPLATE_EVENT_ID = 'get_template_event'

# ** constant: list_templates_event_id
LIST_TEMPLATES_EVENT_ID = 'list_templates_event'

# ** constant: update_template_event_id
UPDATE_TEMPLATE_EVENT_ID = 'update_template_event'

# ** constant: remove_template_event_id
REMOVE_TEMPLATE_EVENT_ID = 'remove_template_event'

# ** constant: apply_template_event_id
APPLY_TEMPLATE_EVENT_ID = 'apply_template_event'

# ** constant: embed_document_sections_event_id
EMBED_DOCUMENT_SECTIONS_EVENT_ID = 'embed_document_sections_event'

# ** constant: search_similar_sections_event_id
SEARCH_SIMILAR_SECTIONS_EVENT_ID = 'search_similar_sections_event'

# ** constant: remove_embedding_event_id
REMOVE_EMBEDDING_EVENT_ID = 'remove_embedding_event'

# ** constant: search_keyword_sections_event_id
SEARCH_KEYWORD_SECTIONS_EVENT_ID = 'search_keyword_sections_event'

# ** constant: search_composed_sections_event_id
SEARCH_COMPOSED_SECTIONS_EVENT_ID = 'search_composed_sections_event'

# ** constant: add_folder_event_id
ADD_FOLDER_EVENT_ID = 'add_folder_event'

# ** constant: get_folder_event_id
GET_FOLDER_EVENT_ID = 'get_folder_event'

# ** constant: set_folder_visibility_event_id
SET_FOLDER_VISIBILITY_EVENT_ID = 'set_folder_visibility_event'

# ** constant: list_folder_contents_event_id
LIST_FOLDER_CONTENTS_EVENT_ID = 'list_folder_contents_event'

# ** constant: move_folder_event_id
MOVE_FOLDER_EVENT_ID = 'move_folder_event'

# ** constant: move_document_event_id
MOVE_DOCUMENT_EVENT_ID = 'move_document_event'

# ** constant: remove_folder_event_id
REMOVE_FOLDER_EVENT_ID = 'remove_folder_event'

# ** constant: import_markdown_document_event_id
IMPORT_MARKDOWN_DOCUMENT_EVENT_ID = 'import_markdown_document_event'

# ** constant: export_document_markdown_event_id
EXPORT_DOCUMENT_MARKDOWN_EVENT_ID = 'export_document_markdown_event'

# ** constant: add_tag_event_id
ADD_TAG_EVENT_ID = 'add_tag_event'

# ** constant: get_tag_event_id
GET_TAG_EVENT_ID = 'get_tag_event'

# ** constant: list_tags_event_id
LIST_TAGS_EVENT_ID = 'list_tags_event'

# ** constant: update_tag_event_id
UPDATE_TAG_EVENT_ID = 'update_tag_event'

# ** constant: remove_tag_event_id
REMOVE_TAG_EVENT_ID = 'remove_tag_event'

# ** constant: tag_document_event_id
TAG_DOCUMENT_EVENT_ID = 'tag_document_event'

# ** constant: untag_document_event_id
UNTAG_DOCUMENT_EVENT_ID = 'untag_document_event'

# ** constant: list_document_tags_event_id
LIST_DOCUMENT_TAGS_EVENT_ID = 'list_document_tags_event'

# ** constant: kb_app_session_id
KB_APP_SESSION_ID = 'kb'

# *** constants (models)

# ** constant: category_service_data
CATEGORY_SERVICE_DATA = create_app_service_dependency_data(
    'tiferet_kb.repos.category',
    'CategoryH5Repository',
)

# ** constant: document_service_data
DOCUMENT_SERVICE_DATA = create_app_service_dependency_data(
    'tiferet_kb.repos.document',
    'DocumentH5Repository',
)

# ** constant: template_service_data
TEMPLATE_SERVICE_DATA = create_app_service_dependency_data(
    'tiferet_kb.repos.template',
    'TemplateH5Repository',
)

# ** constant: folder_service_data
FOLDER_SERVICE_DATA = create_app_service_dependency_data(
    'tiferet_kb.repos.folder',
    'FolderH5Repository',
)

# ** constant: tag_service_data
TAG_SERVICE_DATA = create_app_service_dependency_data(
    'tiferet_kb.repos.tag',
    'TagH5Repository',
)

# ** constant: add_category_event_data
ADD_CATEGORY_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.category',
    'AddCategory',
)

# ** constant: get_category_event_data
GET_CATEGORY_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.category',
    'GetCategory',
)

# ** constant: list_categories_event_data
LIST_CATEGORIES_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.category',
    'ListCategories',
)

# ** constant: update_category_event_data
UPDATE_CATEGORY_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.category',
    'UpdateCategory',
)

# ** constant: remove_category_event_data
REMOVE_CATEGORY_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.category',
    'RemoveCategory',
)

# ** constant: add_section_comment_event_data
ADD_SECTION_COMMENT_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.comment',
    'AddSectionComment',
)

# ** constant: list_section_comments_event_data
LIST_SECTION_COMMENTS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.comment',
    'ListSectionComments',
)

# ** constant: remove_section_comment_event_data
REMOVE_SECTION_COMMENT_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.comment',
    'RemoveSectionComment',
)

# ** constant: add_document_event_data
ADD_DOCUMENT_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'AddDocument',
)

# ** constant: get_document_event_data
GET_DOCUMENT_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'GetDocument',
)

# ** constant: list_documents_event_data
LIST_DOCUMENTS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'ListDocuments',
)

# ** constant: update_document_event_data
UPDATE_DOCUMENT_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'UpdateDocument',
)

# ** constant: set_document_visibility_event_data
SET_DOCUMENT_VISIBILITY_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'SetDocumentVisibility',
)

# ** constant: remove_document_event_data
REMOVE_DOCUMENT_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'RemoveDocument',
)

# ** constant: add_document_section_event_data
ADD_DOCUMENT_SECTION_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'AddDocumentSection',
)

# ** constant: update_document_section_event_data
UPDATE_DOCUMENT_SECTION_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'UpdateDocumentSection',
)

# ** constant: list_document_section_revisions_event_data
LIST_DOCUMENT_SECTION_REVISIONS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'ListDocumentSectionRevisions',
)

# ** constant: restore_document_section_revision_event_data
RESTORE_DOCUMENT_SECTION_REVISION_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'RestoreDocumentSectionRevision',
)

# ** constant: remove_document_section_event_data
REMOVE_DOCUMENT_SECTION_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'RemoveDocumentSection',
)

# ** constant: reorder_document_sections_event_data
REORDER_DOCUMENT_SECTIONS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'ReorderDocumentSections',
)

# ** constant: set_document_property_event_data
SET_DOCUMENT_PROPERTY_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'SetDocumentProperty',
)

# ** constant: remove_document_property_event_data
REMOVE_DOCUMENT_PROPERTY_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document',
    'RemoveDocumentProperty',
)

# ** constant: add_document_link_event_data
ADD_DOCUMENT_LINK_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document_link',
    'AddDocumentLink',
)

# ** constant: remove_document_link_event_data
REMOVE_DOCUMENT_LINK_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document_link',
    'RemoveDocumentLink',
)

# ** constant: list_document_links_event_data
LIST_DOCUMENT_LINKS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.document_link',
    'ListDocumentLinks',
)

# ** constant: add_template_event_data
ADD_TEMPLATE_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.template',
    'AddTemplate',
)

# ** constant: get_template_event_data
GET_TEMPLATE_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.template',
    'GetTemplate',
)

# ** constant: list_templates_event_data
LIST_TEMPLATES_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.template',
    'ListTemplates',
)

# ** constant: update_template_event_data
UPDATE_TEMPLATE_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.template',
    'UpdateTemplate',
)

# ** constant: remove_template_event_data
REMOVE_TEMPLATE_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.template',
    'RemoveTemplate',
)

# ** constant: apply_template_event_data
APPLY_TEMPLATE_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.template',
    'ApplyTemplate',
)

# ** constant: embed_document_sections_event_data
EMBED_DOCUMENT_SECTIONS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.embedding',
    'EmbedDocumentSections',
)

# ** constant: search_similar_sections_event_data
SEARCH_SIMILAR_SECTIONS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.embedding',
    'SearchSimilarSections',
)

# ** constant: remove_embedding_event_data
REMOVE_EMBEDDING_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.embedding',
    'RemoveEmbedding',
)

# ** constant: search_keyword_sections_event_data
SEARCH_KEYWORD_SECTIONS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.search',
    'SearchKeywordSections',
)

# ** constant: search_composed_sections_event_data
SEARCH_COMPOSED_SECTIONS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.search',
    'SearchComposedSections',
)

# ** constant: add_folder_event_data
ADD_FOLDER_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.folder',
    'AddFolder',
)

# ** constant: get_folder_event_data
GET_FOLDER_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.folder',
    'GetFolder',
)

# ** constant: set_folder_visibility_event_data
SET_FOLDER_VISIBILITY_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.folder',
    'SetFolderVisibility',
)

# ** constant: list_folder_contents_event_data
LIST_FOLDER_CONTENTS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.folder',
    'ListFolderContents',
)

# ** constant: move_folder_event_data
MOVE_FOLDER_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.folder',
    'MoveFolder',
)

# ** constant: move_document_event_data
MOVE_DOCUMENT_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.folder',
    'MoveDocument',
)

# ** constant: remove_folder_event_data
REMOVE_FOLDER_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.folder',
    'RemoveFolder',
)

# ** constant: import_markdown_document_event_data
IMPORT_MARKDOWN_DOCUMENT_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.markdown',
    'ImportMarkdownDocument',
)

# ** constant: export_document_markdown_event_data
EXPORT_DOCUMENT_MARKDOWN_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.markdown',
    'ExportDocumentMarkdown',
)

# ** constant: add_tag_event_data
ADD_TAG_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.tag',
    'AddTag',
)

# ** constant: get_tag_event_data
GET_TAG_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.tag',
    'GetTag',
)

# ** constant: list_tags_event_data
LIST_TAGS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.tag',
    'ListTags',
)

# ** constant: update_tag_event_data
UPDATE_TAG_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.tag',
    'UpdateTag',
)

# ** constant: remove_tag_event_data
REMOVE_TAG_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.tag',
    'RemoveTag',
)

# ** constant: tag_document_event_data
TAG_DOCUMENT_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.tag',
    'TagDocument',
)

# ** constant: untag_document_event_data
UNTAG_DOCUMENT_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.tag',
    'UntagDocument',
)

# ** constant: list_document_tags_event_data
LIST_DOCUMENT_TAGS_EVENT_DATA = create_app_service_dependency_data(
    'tiferet_kb.events.tag',
    'ListDocumentTags',
)

# ** constant: kb_app_session_data
KB_APP_SESSION_DATA = create_default_app_session_data(
    'Knowledge Base',
    description='One file holding documents, structure, and retrieval.',
)

# *** constants (groups)

# ** constant: kb_default_services
KB_DEFAULT_SERVICES = {
    CATEGORY_SERVICE_ID: CATEGORY_SERVICE_DATA,
    DOCUMENT_SERVICE_ID: DOCUMENT_SERVICE_DATA,
    TEMPLATE_SERVICE_ID: TEMPLATE_SERVICE_DATA,
    FOLDER_SERVICE_ID: FOLDER_SERVICE_DATA,
    TAG_SERVICE_ID: TAG_SERVICE_DATA,
    ADD_CATEGORY_EVENT_ID: ADD_CATEGORY_EVENT_DATA,
    GET_CATEGORY_EVENT_ID: GET_CATEGORY_EVENT_DATA,
    LIST_CATEGORIES_EVENT_ID: LIST_CATEGORIES_EVENT_DATA,
    UPDATE_CATEGORY_EVENT_ID: UPDATE_CATEGORY_EVENT_DATA,
    REMOVE_CATEGORY_EVENT_ID: REMOVE_CATEGORY_EVENT_DATA,
    ADD_SECTION_COMMENT_EVENT_ID: ADD_SECTION_COMMENT_EVENT_DATA,
    LIST_SECTION_COMMENTS_EVENT_ID: LIST_SECTION_COMMENTS_EVENT_DATA,
    REMOVE_SECTION_COMMENT_EVENT_ID: REMOVE_SECTION_COMMENT_EVENT_DATA,
    ADD_DOCUMENT_EVENT_ID: ADD_DOCUMENT_EVENT_DATA,
    GET_DOCUMENT_EVENT_ID: GET_DOCUMENT_EVENT_DATA,
    LIST_DOCUMENTS_EVENT_ID: LIST_DOCUMENTS_EVENT_DATA,
    UPDATE_DOCUMENT_EVENT_ID: UPDATE_DOCUMENT_EVENT_DATA,
    SET_DOCUMENT_VISIBILITY_EVENT_ID: SET_DOCUMENT_VISIBILITY_EVENT_DATA,
    REMOVE_DOCUMENT_EVENT_ID: REMOVE_DOCUMENT_EVENT_DATA,
    ADD_DOCUMENT_SECTION_EVENT_ID: ADD_DOCUMENT_SECTION_EVENT_DATA,
    UPDATE_DOCUMENT_SECTION_EVENT_ID: UPDATE_DOCUMENT_SECTION_EVENT_DATA,
    LIST_DOCUMENT_SECTION_REVISIONS_EVENT_ID: LIST_DOCUMENT_SECTION_REVISIONS_EVENT_DATA,
    RESTORE_DOCUMENT_SECTION_REVISION_EVENT_ID: RESTORE_DOCUMENT_SECTION_REVISION_EVENT_DATA,
    REMOVE_DOCUMENT_SECTION_EVENT_ID: REMOVE_DOCUMENT_SECTION_EVENT_DATA,
    REORDER_DOCUMENT_SECTIONS_EVENT_ID: REORDER_DOCUMENT_SECTIONS_EVENT_DATA,
    SET_DOCUMENT_PROPERTY_EVENT_ID: SET_DOCUMENT_PROPERTY_EVENT_DATA,
    REMOVE_DOCUMENT_PROPERTY_EVENT_ID: REMOVE_DOCUMENT_PROPERTY_EVENT_DATA,
    ADD_DOCUMENT_LINK_EVENT_ID: ADD_DOCUMENT_LINK_EVENT_DATA,
    REMOVE_DOCUMENT_LINK_EVENT_ID: REMOVE_DOCUMENT_LINK_EVENT_DATA,
    LIST_DOCUMENT_LINKS_EVENT_ID: LIST_DOCUMENT_LINKS_EVENT_DATA,
    ADD_TEMPLATE_EVENT_ID: ADD_TEMPLATE_EVENT_DATA,
    GET_TEMPLATE_EVENT_ID: GET_TEMPLATE_EVENT_DATA,
    LIST_TEMPLATES_EVENT_ID: LIST_TEMPLATES_EVENT_DATA,
    UPDATE_TEMPLATE_EVENT_ID: UPDATE_TEMPLATE_EVENT_DATA,
    REMOVE_TEMPLATE_EVENT_ID: REMOVE_TEMPLATE_EVENT_DATA,
    APPLY_TEMPLATE_EVENT_ID: APPLY_TEMPLATE_EVENT_DATA,
    EMBED_DOCUMENT_SECTIONS_EVENT_ID: EMBED_DOCUMENT_SECTIONS_EVENT_DATA,
    SEARCH_SIMILAR_SECTIONS_EVENT_ID: SEARCH_SIMILAR_SECTIONS_EVENT_DATA,
    REMOVE_EMBEDDING_EVENT_ID: REMOVE_EMBEDDING_EVENT_DATA,
    SEARCH_KEYWORD_SECTIONS_EVENT_ID: SEARCH_KEYWORD_SECTIONS_EVENT_DATA,
    SEARCH_COMPOSED_SECTIONS_EVENT_ID: SEARCH_COMPOSED_SECTIONS_EVENT_DATA,
    ADD_FOLDER_EVENT_ID: ADD_FOLDER_EVENT_DATA,
    GET_FOLDER_EVENT_ID: GET_FOLDER_EVENT_DATA,
    SET_FOLDER_VISIBILITY_EVENT_ID: SET_FOLDER_VISIBILITY_EVENT_DATA,
    LIST_FOLDER_CONTENTS_EVENT_ID: LIST_FOLDER_CONTENTS_EVENT_DATA,
    MOVE_FOLDER_EVENT_ID: MOVE_FOLDER_EVENT_DATA,
    MOVE_DOCUMENT_EVENT_ID: MOVE_DOCUMENT_EVENT_DATA,
    REMOVE_FOLDER_EVENT_ID: REMOVE_FOLDER_EVENT_DATA,
    IMPORT_MARKDOWN_DOCUMENT_EVENT_ID: IMPORT_MARKDOWN_DOCUMENT_EVENT_DATA,
    EXPORT_DOCUMENT_MARKDOWN_EVENT_ID: EXPORT_DOCUMENT_MARKDOWN_EVENT_DATA,
    ADD_TAG_EVENT_ID: ADD_TAG_EVENT_DATA,
    GET_TAG_EVENT_ID: GET_TAG_EVENT_DATA,
    LIST_TAGS_EVENT_ID: LIST_TAGS_EVENT_DATA,
    UPDATE_TAG_EVENT_ID: UPDATE_TAG_EVENT_DATA,
    REMOVE_TAG_EVENT_ID: REMOVE_TAG_EVENT_DATA,
    TAG_DOCUMENT_EVENT_ID: TAG_DOCUMENT_EVENT_DATA,
    UNTAG_DOCUMENT_EVENT_ID: UNTAG_DOCUMENT_EVENT_DATA,
    LIST_DOCUMENT_TAGS_EVENT_ID: LIST_DOCUMENT_TAGS_EVENT_DATA,
}

# ** constant: kb_default_app_sessions
KB_DEFAULT_APP_SESSIONS = {
    KB_APP_SESSION_ID: KB_APP_SESSION_DATA,
}
