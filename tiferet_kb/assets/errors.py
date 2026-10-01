"""tiferet_kb Default Error Definitions"""

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

# *** constants

# ** constant: default_errors
DEFAULT_ERRORS = {

    # * error: KB_DOCUMENT_NOT_FOUND
    KB_DOCUMENT_NOT_FOUND_ID: {
        'id': KB_DOCUMENT_NOT_FOUND_ID,
        'name': 'Document Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Document not found: {document_id}'}
        ]
    },

    # * error: KB_DOCUMENT_ALREADY_EXISTS
    KB_DOCUMENT_ALREADY_EXISTS_ID: {
        'id': KB_DOCUMENT_ALREADY_EXISTS_ID,
        'name': 'Document Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'Document with ID {id} already exists'}
        ]
    },

    # * error: KB_DOCUMENT_LINK_ALREADY_EXISTS
    KB_DOCUMENT_LINK_ALREADY_EXISTS_ID: {
        'id': KB_DOCUMENT_LINK_ALREADY_EXISTS_ID,
        'name': 'Document Link Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'Document link already exists: {id}'}
        ]
    },

    # * error: KB_INVALID_DOCUMENT_LINK
    KB_INVALID_DOCUMENT_LINK_ID: {
        'id': KB_INVALID_DOCUMENT_LINK_ID,
        'name': 'Invalid Document Link',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid document link: {message}'}
        ]
    },

    # * error: KB_DOCUMENT_SECTION_NOT_FOUND
    KB_DOCUMENT_SECTION_NOT_FOUND_ID: {
        'id': KB_DOCUMENT_SECTION_NOT_FOUND_ID,
        'name': 'Document Section Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Document section not found: {section_id}'}
        ]
    },

    # * error: KB_INVALID_DOCUMENT_STATUS
    KB_INVALID_DOCUMENT_STATUS_ID: {
        'id': KB_INVALID_DOCUMENT_STATUS_ID,
        'name': 'Invalid Document Status',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid document status: {status}. Must be draft, published, or archived'}
        ]
    },

    # * error: KB_INVALID_VISIBILITY
    KB_INVALID_VISIBILITY_ID: {
        'id': KB_INVALID_VISIBILITY_ID,
        'name': 'Invalid Visibility',
        'message': [
            {'lang': 'en_US', 'text': KB_INVALID_VISIBILITY_MESSAGE}
        ]
    },

    # * error: KB_INVALID_DOCUMENT_ATTRIBUTE
    KB_INVALID_DOCUMENT_ATTRIBUTE_ID: {
        'id': KB_INVALID_DOCUMENT_ATTRIBUTE_ID,
        'name': 'Invalid Document Attribute',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid document attribute: {attribute}'}
        ]
    },

    # * error: KB_INVALID_PROPERTY_NAME
    KB_INVALID_PROPERTY_NAME_ID: {
        'id': KB_INVALID_PROPERTY_NAME_ID,
        'name': 'Invalid Property Name',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid property name: {name}'}
        ]
    },

    # * error: KB_INVALID_PROPERTY_TYPE
    KB_INVALID_PROPERTY_TYPE_ID: {
        'id': KB_INVALID_PROPERTY_TYPE_ID,
        'name': 'Invalid Property Type',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid property value type: {value_type}. Must be string, number, or boolean'}
        ]
    },

    # * error: KB_INVALID_PROPERTY_VALUE
    KB_INVALID_PROPERTY_VALUE_ID: {
        'id': KB_INVALID_PROPERTY_VALUE_ID,
        'name': 'Invalid Property Value',
        'message': [
            {'lang': 'en_US', 'text': 'Property value does not match value type {value_type}'}
        ]
    },

    # * error: KB_INVALID_PROPERTY_FILTER
    KB_INVALID_PROPERTY_FILTER_ID: {
        'id': KB_INVALID_PROPERTY_FILTER_ID,
        'name': 'Invalid Property Filter',
        'message': [
            {'lang': 'en_US', 'text': 'A property filter requires name, value, and value type'}
        ]
    },

    # * error: KB_INVALID_SECTION_ATTRIBUTE
    KB_INVALID_SECTION_ATTRIBUTE_ID: {
        'id': KB_INVALID_SECTION_ATTRIBUTE_ID,
        'name': 'Invalid Section Attribute',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid section attribute: {attribute}'}
        ]
    },

    # * error: KB_CATEGORY_NOT_FOUND
    KB_CATEGORY_NOT_FOUND_ID: {
        'id': KB_CATEGORY_NOT_FOUND_ID,
        'name': 'Category Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Category not found: {category_id}'}
        ]
    },

    # * error: KB_CATEGORY_ALREADY_EXISTS
    KB_CATEGORY_ALREADY_EXISTS_ID: {
        'id': KB_CATEGORY_ALREADY_EXISTS_ID,
        'name': 'Category Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'Category with ID {id} already exists'}
        ]
    },

    # * error: KB_CATEGORY_IN_USE
    KB_CATEGORY_IN_USE_ID: {
        'id': KB_CATEGORY_IN_USE_ID,
        'name': 'Category In Use',
        'message': [
            {'lang': 'en_US', 'text': 'Category {id} is referenced by existing documents'}
        ]
    },

    # * error: KB_INVALID_CATEGORY_ATTRIBUTE
    KB_INVALID_CATEGORY_ATTRIBUTE_ID: {
        'id': KB_INVALID_CATEGORY_ATTRIBUTE_ID,
        'name': 'Invalid Category Attribute',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid category attribute: {attribute}'}
        ]
    },

    # * error: KB_TEMPLATE_NOT_FOUND
    KB_TEMPLATE_NOT_FOUND_ID: {
        'id': KB_TEMPLATE_NOT_FOUND_ID,
        'name': 'Template Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Template not found: {template_id}'}
        ]
    },

    # * error: KB_TEMPLATE_ALREADY_EXISTS
    KB_TEMPLATE_ALREADY_EXISTS_ID: {
        'id': KB_TEMPLATE_ALREADY_EXISTS_ID,
        'name': 'Template Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'Template with ID {id} already exists'}
        ]
    },

    # * error: KB_FOLDER_NOT_FOUND
    KB_FOLDER_NOT_FOUND_ID: {
        'id': KB_FOLDER_NOT_FOUND_ID,
        'name': 'Folder Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Folder not found: {folder_id}'}
        ]
    },

    # * error: KB_FOLDER_ALREADY_EXISTS
    KB_FOLDER_ALREADY_EXISTS_ID: {
        'id': KB_FOLDER_ALREADY_EXISTS_ID,
        'name': 'Folder Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'Folder with ID {id} already exists'}
        ]
    },

    # * error: KB_FOLDER_CIRCULAR_REFERENCE
    KB_FOLDER_CIRCULAR_REFERENCE_ID: {
        'id': KB_FOLDER_CIRCULAR_REFERENCE_ID,
        'name': 'Folder Circular Reference',
        'message': [
            {'lang': 'en_US', 'text': 'Cannot move folder {folder_id} to create a circular reference'}
        ]
    },

    # * error: KB_FOLDER_NOT_EMPTY
    KB_FOLDER_NOT_EMPTY_ID: {
        'id': KB_FOLDER_NOT_EMPTY_ID,
        'name': 'Folder Not Empty',
        'message': [
            {'lang': 'en_US', 'text': 'Folder {folder_id} contains documents or subfolders'}
        ]
    },

    # * error: KB_INVALID_CONTENT_TYPE
    KB_INVALID_CONTENT_TYPE_ID: {
        'id': KB_INVALID_CONTENT_TYPE_ID,
        'name': 'Invalid Content Type',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid content type: {content_type}. Must be text, markdown, code, table, or image'}
        ]
    },

    # * error: KB_EMBEDDING_NOT_FOUND
    KB_EMBEDDING_NOT_FOUND_ID: {
        'id': KB_EMBEDDING_NOT_FOUND_ID,
        'name': 'Embedding Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Embedding not found for section: {section_id}'}
        ]
    },

    # * error: KB_EMBEDDING_DIMENSION_MISMATCH
    KB_EMBEDDING_DIMENSION_MISMATCH_ID: {
        'id': KB_EMBEDDING_DIMENSION_MISMATCH_ID,
        'name': 'Embedding Dimension Mismatch',
        'message': [
            {'lang': 'en_US', 'text': 'Embedding dimension mismatch: expected {expected}, got {actual}'}
        ]
    },

    # * error: KB_SECTION_NOT_EMBEDDED
    KB_SECTION_NOT_EMBEDDED_ID: {
        'id': KB_SECTION_NOT_EMBEDDED_ID,
        'name': 'Section Not Embedded',
        'message': [
            {'lang': 'en_US', 'text': 'Section {section_id} has no embedding'}
        ]
    },

    # * error: KB_TAG_NOT_FOUND
    KB_TAG_NOT_FOUND_ID: {
        'id': KB_TAG_NOT_FOUND_ID,
        'name': 'Tag Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Tag not found: {tag_id}'}
        ]
    },

    # * error: KB_TAG_ALREADY_EXISTS
    KB_TAG_ALREADY_EXISTS_ID: {
        'id': KB_TAG_ALREADY_EXISTS_ID,
        'name': 'Tag Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'Tag with ID {id} already exists'}
        ]
    },

    # * error: KB_TAG_IN_USE
    KB_TAG_IN_USE_ID: {
        'id': KB_TAG_IN_USE_ID,
        'name': 'Tag In Use',
        'message': [
            {'lang': 'en_US', 'text': 'Tag {id} is carried by existing documents'}
        ]
    },

    # * error: KB_INVALID_TAG_ATTRIBUTE
    KB_INVALID_TAG_ATTRIBUTE_ID: {
        'id': KB_INVALID_TAG_ATTRIBUTE_ID,
        'name': 'Invalid Tag Attribute',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid tag attribute: {attribute}'}
        ]
    },

    # * error: KB_INVALID_SECTION_COMMENT
    KB_INVALID_SECTION_COMMENT_ID: {
        'id': KB_INVALID_SECTION_COMMENT_ID,
        'name': 'Invalid Section Comment',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid section comment: {field}'}
        ]
    },

    # * error: KB_SECTION_COMMENT_ALREADY_EXISTS
    KB_SECTION_COMMENT_ALREADY_EXISTS_ID: {
        'id': KB_SECTION_COMMENT_ALREADY_EXISTS_ID,
        'name': 'Section Comment Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'Section comment with ID {id} already exists'}
        ]
    },

    # * error: KB_SECTION_COMMENT_HAS_REPLIES
    KB_SECTION_COMMENT_HAS_REPLIES_ID: {
        'id': KB_SECTION_COMMENT_HAS_REPLIES_ID,
        'name': 'Section Comment Has Replies',
        'message': [
            {'lang': 'en_US', 'text': 'Section comment {id} still has replies'}
        ]
    },
}
