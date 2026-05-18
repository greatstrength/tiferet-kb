"""tiferet_kb Document Domain"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any, List, Optional
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject

from .segment import Paragraph

# *** models

# ** model: document_section
class DocumentSection(DomainObject):
    '''
    A section within a knowledge base document.

    Each section is stored as an HDF5 group node with metadata attributes
    and a single flat segments table containing rich-text content decomposed
    into paragraphs and text segments with formatting metadata.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this section.',
    )

    # * attribute: document_id
    document_id: str = Field(
        ...,
        description='UUID of the parent document.',
    )

    # * attribute: title
    title: str = Field(
        ...,
        description='Section heading.',
    )

    # * attribute: heading_level
    heading_level: int = Field(
        default=2,
        description='Heading level (1-6).',
    )

    # * attribute: icon
    icon: Optional[str] = Field(
        default=None,
        description='Optional icon identifier for the section.',
    )

    # * attribute: content_type
    content_type: str = Field(
        default='markdown',
        description='Section rendering mode: markdown, text, or code.',
    )

    # * attribute: position
    position: int = Field(
        ...,
        description='Zero-based ordering position within the document.',
    )

    # * attribute: created_at
    created_at: str = Field(
        ...,
        description='ISO 8601 creation timestamp.',
    )

    # * attribute: updated_at
    updated_at: str = Field(
        ...,
        description='ISO 8601 last-updated timestamp.',
    )

    # * attribute: paragraphs
    paragraphs: List[Paragraph] = Field(
        default_factory=list,
        description='Ordered list of paragraphs with rich-text segments.',
    )

    # * method: _derive_defaults (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_defaults(cls, data: Any) -> Any:
        '''
        Derive default values for id, created_at, and updated_at when absent.

        :param data: The raw input data.
        :type data: Any
        :return: The augmented input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Generate a UUID if id is not provided.
        if not data.get('id'):
            data['id'] = str(uuid4())

        # Set timestamps if not provided.
        now = datetime.now(timezone.utc).isoformat()
        if not data.get('created_at'):
            data['created_at'] = now
        if not data.get('updated_at'):
            data['updated_at'] = now

        # Return the augmented data.
        return data


# ** model: document
class Document(DomainObject):
    '''
    A knowledge base document.

    Documents are the primary content objects in the knowledge base,
    composed of ordered sections and optionally classified by category,
    sourced from a template, and placed within a folder.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this document.',
    )

    # * attribute: title
    title: str = Field(
        ...,
        description='Document title.',
    )

    # * attribute: category_id
    category_id: Optional[str] = Field(
        default=None,
        description='Optional category identifier for classification.',
    )

    # * attribute: template_id
    template_id: Optional[str] = Field(
        default=None,
        description='Optional template identifier used to create this document.',
    )

    # * attribute: folder_id
    folder_id: Optional[str] = Field(
        default=None,
        description='Optional folder identifier for organization.',
    )

    # * attribute: status
    status: str = Field(
        default='draft',
        description='Document status: draft, published, or archived.',
    )

    # * attribute: created_at
    created_at: str = Field(
        ...,
        description='ISO 8601 creation timestamp.',
    )

    # * attribute: updated_at
    updated_at: str = Field(
        ...,
        description='ISO 8601 last-updated timestamp.',
    )

    # * attribute: sections
    sections: List[DocumentSection] = Field(
        default_factory=list,
        description='Ordered list of document sections, populated by the service layer.',
    )

    # * method: _derive_defaults (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_defaults(cls, data: Any) -> Any:
        '''
        Derive default values for id, status, created_at, and updated_at when absent.

        :param data: The raw input data.
        :type data: Any
        :return: The augmented input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Generate a UUID if id is not provided.
        if not data.get('id'):
            data['id'] = str(uuid4())

        # Default status to 'draft'.
        if not data.get('status'):
            data['status'] = 'draft'

        # Set timestamps if not provided.
        now = datetime.now(timezone.utc).isoformat()
        if not data.get('created_at'):
            data['created_at'] = now
        if not data.get('updated_at'):
            data['updated_at'] = now

        # Return the augmented data.
        return data

    # * method: get_section
    def get_section(self, position: int) -> Optional[DocumentSection]:
        '''
        Get the document section at the given position.

        :param position: The index of the section to retrieve.
        :type position: int
        :return: The DocumentSection at the position, or None.
        :rtype: DocumentSection | None
        '''

        # Attempt to retrieve the section, returning None if out of range.
        try:
            return self.sections[position]
        except (IndexError, TypeError):
            return None

    # * method: section_count
    def section_count(self) -> int:
        '''
        Return the number of sections in this document.

        :return: The section count.
        :rtype: int
        '''

        # Return the length of the sections list.
        return len(self.sections)
