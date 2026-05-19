"""tiferet_kb Default Error Definitions"""

# *** imports

# ** app
from .constants import (
    KB_DOCUMENT_NOT_FOUND_ID,
    KB_DOCUMENT_ALREADY_EXISTS_ID,
    KB_DOCUMENT_SECTION_NOT_FOUND_ID,
    KB_INVALID_DOCUMENT_STATUS_ID,
    KB_INVALID_DOCUMENT_ATTRIBUTE_ID,
    KB_INVALID_SECTION_ATTRIBUTE_ID,
    KB_CATEGORY_NOT_FOUND_ID,
    KB_CATEGORY_ALREADY_EXISTS_ID,
    KB_CATEGORY_IN_USE_ID,
    KB_INVALID_CATEGORY_ATTRIBUTE_ID,
    KB_TEMPLATE_NOT_FOUND_ID,
    KB_TEMPLATE_ALREADY_EXISTS_ID,
    KB_FOLDER_NOT_FOUND_ID,
    KB_FOLDER_ALREADY_EXISTS_ID,
    KB_FOLDER_CIRCULAR_REFERENCE_ID,
    KB_FOLDER_NOT_EMPTY_ID,
    KB_INVALID_CONTENT_TYPE_ID,
    KB_EMBEDDING_NOT_FOUND_ID,
    KB_EMBEDDING_DIMENSION_MISMATCH_ID,
    KB_SECTION_NOT_EMBEDDED_ID,
)

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

    # * error: KB_INVALID_DOCUMENT_ATTRIBUTE
    KB_INVALID_DOCUMENT_ATTRIBUTE_ID: {
        'id': KB_INVALID_DOCUMENT_ATTRIBUTE_ID,
        'name': 'Invalid Document Attribute',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid document attribute: {attribute}'}
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
}
