"""tiferet_kb Error Catalog"""

# *** imports

# ** app
from tiferet.assets.core import EN_US, create_default_error_data

# *** constants (ids)

# ** constant: kb_document_not_found_id
KB_DOCUMENT_NOT_FOUND_ID = 'KB_DOCUMENT_NOT_FOUND'

# ** constant: kb_document_already_exists_id
KB_DOCUMENT_ALREADY_EXISTS_ID = 'KB_DOCUMENT_ALREADY_EXISTS'

# ** constant: kb_document_link_already_exists_id
KB_DOCUMENT_LINK_ALREADY_EXISTS_ID = 'KB_DOCUMENT_LINK_ALREADY_EXISTS'

# ** constant: kb_invalid_document_link_id
KB_INVALID_DOCUMENT_LINK_ID = 'KB_INVALID_DOCUMENT_LINK'

# ** constant: kb_document_section_not_found_id
KB_DOCUMENT_SECTION_NOT_FOUND_ID = 'KB_DOCUMENT_SECTION_NOT_FOUND'

# ** constant: kb_section_revision_not_found_id
KB_SECTION_REVISION_NOT_FOUND_ID = 'KB_SECTION_REVISION_NOT_FOUND'

# ** constant: kb_invalid_document_status_id
KB_INVALID_DOCUMENT_STATUS_ID = 'KB_INVALID_DOCUMENT_STATUS'

# ** constant: kb_invalid_visibility_id
KB_INVALID_VISIBILITY_ID = 'KB_INVALID_VISIBILITY'

# ** constant: kb_invalid_visibility_message
KB_INVALID_VISIBILITY_MESSAGE = (
    'Invalid visibility: {visibility}. Must be public, private, or restricted'
)

# ** constant: kb_invalid_document_attribute_id
KB_INVALID_DOCUMENT_ATTRIBUTE_ID = 'KB_INVALID_DOCUMENT_ATTRIBUTE'

# ** constant: kb_invalid_property_name_id
KB_INVALID_PROPERTY_NAME_ID = 'KB_INVALID_PROPERTY_NAME'

# ** constant: kb_invalid_property_type_id
KB_INVALID_PROPERTY_TYPE_ID = 'KB_INVALID_PROPERTY_TYPE'

# ** constant: kb_invalid_property_value_id
KB_INVALID_PROPERTY_VALUE_ID = 'KB_INVALID_PROPERTY_VALUE'

# ** constant: kb_invalid_property_filter_id
KB_INVALID_PROPERTY_FILTER_ID = 'KB_INVALID_PROPERTY_FILTER'

# ** constant: kb_invalid_section_attribute_id
KB_INVALID_SECTION_ATTRIBUTE_ID = 'KB_INVALID_SECTION_ATTRIBUTE'

# ** constant: kb_category_not_found_id
KB_CATEGORY_NOT_FOUND_ID = 'KB_CATEGORY_NOT_FOUND'

# ** constant: kb_category_already_exists_id
KB_CATEGORY_ALREADY_EXISTS_ID = 'KB_CATEGORY_ALREADY_EXISTS'

# ** constant: kb_category_in_use_id
KB_CATEGORY_IN_USE_ID = 'KB_CATEGORY_IN_USE'

# ** constant: kb_invalid_category_attribute_id
KB_INVALID_CATEGORY_ATTRIBUTE_ID = 'KB_INVALID_CATEGORY_ATTRIBUTE'

# ** constant: kb_template_not_found_id
KB_TEMPLATE_NOT_FOUND_ID = 'KB_TEMPLATE_NOT_FOUND'

# ** constant: kb_template_already_exists_id
KB_TEMPLATE_ALREADY_EXISTS_ID = 'KB_TEMPLATE_ALREADY_EXISTS'

# ** constant: kb_folder_not_found_id
KB_FOLDER_NOT_FOUND_ID = 'KB_FOLDER_NOT_FOUND'

# ** constant: kb_folder_already_exists_id
KB_FOLDER_ALREADY_EXISTS_ID = 'KB_FOLDER_ALREADY_EXISTS'

# ** constant: kb_folder_circular_reference_id
KB_FOLDER_CIRCULAR_REFERENCE_ID = 'KB_FOLDER_CIRCULAR_REFERENCE'

# ** constant: kb_folder_not_empty_id
KB_FOLDER_NOT_EMPTY_ID = 'KB_FOLDER_NOT_EMPTY'

# ** constant: kb_invalid_content_type_id
KB_INVALID_CONTENT_TYPE_ID = 'KB_INVALID_CONTENT_TYPE'

# ** constant: kb_embedding_not_found_id
KB_EMBEDDING_NOT_FOUND_ID = 'KB_EMBEDDING_NOT_FOUND'

# ** constant: kb_embedding_dimension_mismatch_id
KB_EMBEDDING_DIMENSION_MISMATCH_ID = 'KB_EMBEDDING_DIMENSION_MISMATCH'

# ** constant: kb_section_not_embedded_id
KB_SECTION_NOT_EMBEDDED_ID = 'KB_SECTION_NOT_EMBEDDED'

# ** constant: kb_tag_not_found_id
KB_TAG_NOT_FOUND_ID = 'KB_TAG_NOT_FOUND'

# ** constant: kb_tag_already_exists_id
KB_TAG_ALREADY_EXISTS_ID = 'KB_TAG_ALREADY_EXISTS'

# ** constant: kb_tag_in_use_id
KB_TAG_IN_USE_ID = 'KB_TAG_IN_USE'

# ** constant: kb_invalid_tag_attribute_id
KB_INVALID_TAG_ATTRIBUTE_ID = 'KB_INVALID_TAG_ATTRIBUTE'

# ** constant: kb_invalid_section_comment_id
KB_INVALID_SECTION_COMMENT_ID = 'KB_INVALID_SECTION_COMMENT'

# ** constant: kb_section_comment_already_exists_id
KB_SECTION_COMMENT_ALREADY_EXISTS_ID = 'KB_SECTION_COMMENT_ALREADY_EXISTS'

# ** constant: kb_section_comment_has_replies_id
KB_SECTION_COMMENT_HAS_REPLIES_ID = 'KB_SECTION_COMMENT_HAS_REPLIES'

# *** constants (models)

# ** constant: kb_document_not_found_data
KB_DOCUMENT_NOT_FOUND_DATA = create_default_error_data(
    'Document Not Found',
    [(EN_US, 'Document not found: {document_id}')],
)

# ** constant: kb_document_already_exists_data
KB_DOCUMENT_ALREADY_EXISTS_DATA = create_default_error_data(
    'Document Already Exists',
    [(EN_US, 'Document with ID {id} already exists')],
)

# ** constant: kb_document_link_already_exists_data
KB_DOCUMENT_LINK_ALREADY_EXISTS_DATA = create_default_error_data(
    'Document Link Already Exists',
    [(EN_US, 'Document link already exists: {id}')],
)

# ** constant: kb_invalid_document_link_data
KB_INVALID_DOCUMENT_LINK_DATA = create_default_error_data(
    'Invalid Document Link',
    [(EN_US, 'Invalid document link: {message}')],
)

# ** constant: kb_document_section_not_found_data
KB_DOCUMENT_SECTION_NOT_FOUND_DATA = create_default_error_data(
    'Document Section Not Found',
    [(EN_US, 'Document section not found: {section_id}')],
)

# ** constant: kb_section_revision_not_found_data
KB_SECTION_REVISION_NOT_FOUND_DATA = create_default_error_data(
    'Section Revision Not Found',
    [(EN_US, 'Section revision not found: {number}')],
)

# ** constant: kb_invalid_document_status_data
KB_INVALID_DOCUMENT_STATUS_DATA = create_default_error_data(
    'Invalid Document Status',
    [(EN_US, 'Invalid document status: {status}. Must be draft, published, or archived')],
)

# ** constant: kb_invalid_visibility_data
KB_INVALID_VISIBILITY_DATA = create_default_error_data(
    'Invalid Visibility',
    [(EN_US, KB_INVALID_VISIBILITY_MESSAGE)],
)

# ** constant: kb_invalid_document_attribute_data
KB_INVALID_DOCUMENT_ATTRIBUTE_DATA = create_default_error_data(
    'Invalid Document Attribute',
    [(EN_US, 'Invalid document attribute: {attribute}')],
)

# ** constant: kb_invalid_property_name_data
KB_INVALID_PROPERTY_NAME_DATA = create_default_error_data(
    'Invalid Property Name',
    [(EN_US, 'Invalid property name: {name}')],
)

# ** constant: kb_invalid_property_type_data
KB_INVALID_PROPERTY_TYPE_DATA = create_default_error_data(
    'Invalid Property Type',
    [(EN_US, 'Invalid property value type: {value_type}. Must be string, number, or boolean')],
)

# ** constant: kb_invalid_property_value_data
KB_INVALID_PROPERTY_VALUE_DATA = create_default_error_data(
    'Invalid Property Value',
    [(EN_US, 'Property value does not match value type {value_type}')],
)

# ** constant: kb_invalid_property_filter_data
KB_INVALID_PROPERTY_FILTER_DATA = create_default_error_data(
    'Invalid Property Filter',
    [(EN_US, 'A property filter requires name, value, and value type')],
)

# ** constant: kb_invalid_section_attribute_data
KB_INVALID_SECTION_ATTRIBUTE_DATA = create_default_error_data(
    'Invalid Section Attribute',
    [(EN_US, 'Invalid section attribute: {attribute}')],
)

# ** constant: kb_category_not_found_data
KB_CATEGORY_NOT_FOUND_DATA = create_default_error_data(
    'Category Not Found',
    [(EN_US, 'Category not found: {category_id}')],
)

# ** constant: kb_category_already_exists_data
KB_CATEGORY_ALREADY_EXISTS_DATA = create_default_error_data(
    'Category Already Exists',
    [(EN_US, 'Category with ID {id} already exists')],
)

# ** constant: kb_category_in_use_data
KB_CATEGORY_IN_USE_DATA = create_default_error_data(
    'Category In Use',
    [(EN_US, 'Category {id} is referenced by existing documents')],
)

# ** constant: kb_invalid_category_attribute_data
KB_INVALID_CATEGORY_ATTRIBUTE_DATA = create_default_error_data(
    'Invalid Category Attribute',
    [(EN_US, 'Invalid category attribute: {attribute}')],
)

# ** constant: kb_template_not_found_data
KB_TEMPLATE_NOT_FOUND_DATA = create_default_error_data(
    'Template Not Found',
    [(EN_US, 'Template not found: {template_id}')],
)

# ** constant: kb_template_already_exists_data
KB_TEMPLATE_ALREADY_EXISTS_DATA = create_default_error_data(
    'Template Already Exists',
    [(EN_US, 'Template with ID {id} already exists')],
)

# ** constant: kb_folder_not_found_data
KB_FOLDER_NOT_FOUND_DATA = create_default_error_data(
    'Folder Not Found',
    [(EN_US, 'Folder not found: {folder_id}')],
)

# ** constant: kb_folder_already_exists_data
KB_FOLDER_ALREADY_EXISTS_DATA = create_default_error_data(
    'Folder Already Exists',
    [(EN_US, 'Folder with ID {id} already exists')],
)

# ** constant: kb_folder_circular_reference_data
KB_FOLDER_CIRCULAR_REFERENCE_DATA = create_default_error_data(
    'Folder Circular Reference',
    [(EN_US, 'Cannot move folder {folder_id} to create a circular reference')],
)

# ** constant: kb_folder_not_empty_data
KB_FOLDER_NOT_EMPTY_DATA = create_default_error_data(
    'Folder Not Empty',
    [(EN_US, 'Folder {folder_id} contains documents or subfolders')],
)

# ** constant: kb_invalid_content_type_data
KB_INVALID_CONTENT_TYPE_DATA = create_default_error_data(
    'Invalid Content Type',
    [(EN_US, 'Invalid content type: {content_type}. Must be text, markdown, code, table, or image')],
)

# ** constant: kb_embedding_not_found_data
KB_EMBEDDING_NOT_FOUND_DATA = create_default_error_data(
    'Embedding Not Found',
    [(EN_US, 'Embedding not found for section: {section_id}')],
)

# ** constant: kb_embedding_dimension_mismatch_data
KB_EMBEDDING_DIMENSION_MISMATCH_DATA = create_default_error_data(
    'Embedding Dimension Mismatch',
    [(EN_US, 'Embedding dimension mismatch: expected {expected}, got {actual}')],
)

# ** constant: kb_section_not_embedded_data
KB_SECTION_NOT_EMBEDDED_DATA = create_default_error_data(
    'Section Not Embedded',
    [(EN_US, 'Section {section_id} has no embedding')],
)

# ** constant: kb_tag_not_found_data
KB_TAG_NOT_FOUND_DATA = create_default_error_data(
    'Tag Not Found',
    [(EN_US, 'Tag not found: {tag_id}')],
)

# ** constant: kb_tag_already_exists_data
KB_TAG_ALREADY_EXISTS_DATA = create_default_error_data(
    'Tag Already Exists',
    [(EN_US, 'Tag with ID {id} already exists')],
)

# ** constant: kb_tag_in_use_data
KB_TAG_IN_USE_DATA = create_default_error_data(
    'Tag In Use',
    [(EN_US, 'Tag {id} is carried by existing documents')],
)

# ** constant: kb_invalid_tag_attribute_data
KB_INVALID_TAG_ATTRIBUTE_DATA = create_default_error_data(
    'Invalid Tag Attribute',
    [(EN_US, 'Invalid tag attribute: {attribute}')],
)

# ** constant: kb_invalid_section_comment_data
KB_INVALID_SECTION_COMMENT_DATA = create_default_error_data(
    'Invalid Section Comment',
    [(EN_US, 'Invalid section comment: {field}')],
)

# ** constant: kb_section_comment_already_exists_data
KB_SECTION_COMMENT_ALREADY_EXISTS_DATA = create_default_error_data(
    'Section Comment Already Exists',
    [(EN_US, 'Section comment with ID {id} already exists')],
)

# ** constant: kb_section_comment_has_replies_data
KB_SECTION_COMMENT_HAS_REPLIES_DATA = create_default_error_data(
    'Section Comment Has Replies',
    [(EN_US, 'Section comment {id} still has replies')],
)

# *** constants (groups)

# ** constant: kb_default_errors
KB_DEFAULT_ERRORS = {
    KB_DOCUMENT_NOT_FOUND_ID: KB_DOCUMENT_NOT_FOUND_DATA,
    KB_DOCUMENT_ALREADY_EXISTS_ID: KB_DOCUMENT_ALREADY_EXISTS_DATA,
    KB_DOCUMENT_LINK_ALREADY_EXISTS_ID: KB_DOCUMENT_LINK_ALREADY_EXISTS_DATA,
    KB_INVALID_DOCUMENT_LINK_ID: KB_INVALID_DOCUMENT_LINK_DATA,
    KB_DOCUMENT_SECTION_NOT_FOUND_ID: KB_DOCUMENT_SECTION_NOT_FOUND_DATA,
    KB_SECTION_REVISION_NOT_FOUND_ID: KB_SECTION_REVISION_NOT_FOUND_DATA,
    KB_INVALID_DOCUMENT_STATUS_ID: KB_INVALID_DOCUMENT_STATUS_DATA,
    KB_INVALID_VISIBILITY_ID: KB_INVALID_VISIBILITY_DATA,
    KB_INVALID_DOCUMENT_ATTRIBUTE_ID: KB_INVALID_DOCUMENT_ATTRIBUTE_DATA,
    KB_INVALID_PROPERTY_NAME_ID: KB_INVALID_PROPERTY_NAME_DATA,
    KB_INVALID_PROPERTY_TYPE_ID: KB_INVALID_PROPERTY_TYPE_DATA,
    KB_INVALID_PROPERTY_VALUE_ID: KB_INVALID_PROPERTY_VALUE_DATA,
    KB_INVALID_PROPERTY_FILTER_ID: KB_INVALID_PROPERTY_FILTER_DATA,
    KB_INVALID_SECTION_ATTRIBUTE_ID: KB_INVALID_SECTION_ATTRIBUTE_DATA,
    KB_CATEGORY_NOT_FOUND_ID: KB_CATEGORY_NOT_FOUND_DATA,
    KB_CATEGORY_ALREADY_EXISTS_ID: KB_CATEGORY_ALREADY_EXISTS_DATA,
    KB_CATEGORY_IN_USE_ID: KB_CATEGORY_IN_USE_DATA,
    KB_INVALID_CATEGORY_ATTRIBUTE_ID: KB_INVALID_CATEGORY_ATTRIBUTE_DATA,
    KB_TEMPLATE_NOT_FOUND_ID: KB_TEMPLATE_NOT_FOUND_DATA,
    KB_TEMPLATE_ALREADY_EXISTS_ID: KB_TEMPLATE_ALREADY_EXISTS_DATA,
    KB_FOLDER_NOT_FOUND_ID: KB_FOLDER_NOT_FOUND_DATA,
    KB_FOLDER_ALREADY_EXISTS_ID: KB_FOLDER_ALREADY_EXISTS_DATA,
    KB_FOLDER_CIRCULAR_REFERENCE_ID: KB_FOLDER_CIRCULAR_REFERENCE_DATA,
    KB_FOLDER_NOT_EMPTY_ID: KB_FOLDER_NOT_EMPTY_DATA,
    KB_INVALID_CONTENT_TYPE_ID: KB_INVALID_CONTENT_TYPE_DATA,
    KB_EMBEDDING_NOT_FOUND_ID: KB_EMBEDDING_NOT_FOUND_DATA,
    KB_EMBEDDING_DIMENSION_MISMATCH_ID: KB_EMBEDDING_DIMENSION_MISMATCH_DATA,
    KB_SECTION_NOT_EMBEDDED_ID: KB_SECTION_NOT_EMBEDDED_DATA,
    KB_TAG_NOT_FOUND_ID: KB_TAG_NOT_FOUND_DATA,
    KB_TAG_ALREADY_EXISTS_ID: KB_TAG_ALREADY_EXISTS_DATA,
    KB_TAG_IN_USE_ID: KB_TAG_IN_USE_DATA,
    KB_INVALID_TAG_ATTRIBUTE_ID: KB_INVALID_TAG_ATTRIBUTE_DATA,
    KB_INVALID_SECTION_COMMENT_ID: KB_INVALID_SECTION_COMMENT_DATA,
    KB_SECTION_COMMENT_ALREADY_EXISTS_ID: KB_SECTION_COMMENT_ALREADY_EXISTS_DATA,
    KB_SECTION_COMMENT_HAS_REPLIES_ID: KB_SECTION_COMMENT_HAS_REPLIES_DATA,
}
