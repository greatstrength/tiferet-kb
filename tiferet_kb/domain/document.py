"""tiferet_kb Document Domain"""

# *** imports

# ** core
import math
from datetime import datetime, timezone
from typing import Any, List, Optional
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject, ModelError

from ..assets import error as err
from .segment import Paragraph

# *** constants

# ** constant: property_value_types
PROPERTY_VALUE_TYPES = (
    'string',
    'number',
    'boolean',
)

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
        default=0,
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

    # * method: content (property)
    @property
    def content(self) -> str:
        '''
        Render this section's paragraphs as markdown text.

        The value is derived. It is not a field, has no setter, and is
        omitted from ``model_dump``.

        :return: The section body, without a heading or a trailing newline.
        :rtype: str
        '''

        # One renderer for the property and for export.
        from ..utils.markdown import render_section
        return render_section(self)

    # * method: _derive_defaults (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_defaults(cls, data: Any) -> Any:
        '''
        Derive defaults and consume a content string into paragraphs.

        ``id``, ``created_at``, and ``updated_at`` are filled when absent.
        A ``content`` string is parsed when paragraphs are absent or empty,
        then removed so it is not a stored field. Non-empty paragraphs win.

        :param data: The raw input data.
        :type data: Any
        :return: The augmented input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Generate a UUID if id is not provided. Parse needs the identifier.
        if not data.get('id'):
            data['id'] = str(uuid4())

        # Consume content before extra='forbid'. It is not a stored field.
        if 'content' in data:
            content = data.pop('content')
            if not isinstance(content, str):
                raise ValueError('content must be a string.')

            # Parse only when paragraphs are absent or empty.
            if content and not data.get('paragraphs'):
                from ..utils.markdown import parse_content_to_paragraphs
                data['paragraphs'] = parse_content_to_paragraphs(content, data['id'])

        # Set timestamps if not provided.
        now = datetime.now(timezone.utc).isoformat()
        if not data.get('created_at'):
            data['created_at'] = now
        if not data.get('updated_at'):
            data['updated_at'] = now

        # Return the augmented data.
        return data

# ** model: document_property
class DocumentProperty(DomainObject):
    '''
    A named typed value on a document, outside the fixed header columns.

    One name has one value. The type is chosen by the caller and is not
    inferred. A property does not alias title, status, category, template,
    or folder, and it is not a tag, a fact type, or a schema entry.
    '''

    # * attribute: document_id
    document_id: str = Field(
        ...,
        description='UUID of the document this property belongs to.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='Stored property name. Stripped once; case and internal spaces stay.',
    )

    # * attribute: value
    value: Any = Field(
        ...,
        description='The property value. A string, a finite number, or a boolean.',
    )

    # * attribute: value_type
    value_type: str = Field(
        ...,
        description='Declared type: string, number, or boolean. Not inferred.',
    )

    # * method: _normalize_name (validator)
    @model_validator(mode='before')
    @classmethod
    def _normalize_name(cls, data: Any) -> Any:
        '''
        Strip the property name once before field validation.

        :param data: The raw input data.
        :type data: Any
        :return: The input data with a stripped name when the name is a string.
        :rtype: Any
        '''

        # Leave non-mapping input for Pydantic to handle.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Strip a string name once. Internal spaces and case stay.
        name = data.get('name')
        if isinstance(name, str):
            data['name'] = name.strip()

        # Return the canonicalized input.
        return data

    # * method: _validate_property (validator)
    @model_validator(mode='after')
    def _validate_property(self) -> 'DocumentProperty':
        '''
        Refuse a property whose name, type, or value is not storable.

        :return: The validated property.
        :rtype: DocumentProperty
        '''

        # Refuse an invalid property as a model defect, not a domain outcome.
        type(self).rejection(self.name, self.value, self.value_type)

        # Return the valid property.
        return self

    # * method: value_matches
    @classmethod
    def value_matches(cls, value: Any, value_type: str) -> bool:
        '''
        Return whether ``value`` is a legal instance of ``value_type``.

        A boolean is not a number. A number is not a boolean. A string is
        not coerced, and ``''`` is a string. ``None`` is never a value.

        :param value: The candidate value.
        :type value: Any
        :param value_type: The declared type.
        :type value_type: str
        :return: True when the value matches the type.
        :rtype: bool
        '''

        # None is not a value. Clearing a field is remove, not a null write.
        if value is None:
            return False

        # A string is a str, including the empty string. It is not stripped.
        if value_type == 'string':
            return isinstance(value, str)

        # Check bool before int. bool is a subclass of int.
        if value_type == 'boolean':
            return isinstance(value, bool)

        # A number is a finite int or float, never a bool.
        if value_type == 'number':
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return False
            try:
                return math.isfinite(float(value))
            except OverflowError:
                return False

        # An unknown type does not match.
        return False

    # * method: rejection
    @classmethod
    def rejection(cls, name: Any, value: Any, value_type: Any) -> None:
        '''
        Raise ModelError when a property name, type, or value cannot be stored.

        The name is judged after one strip. The type is not inferred from the value.

        :param name: The candidate name.
        :type name: Any
        :param value: The candidate value.
        :type value: Any
        :param value_type: The candidate type.
        :type value_type: Any
        :return: None
        :rtype: None
        '''

        # Empty or non-string names are invalid. The stored form is the strip.
        if not isinstance(name, str) or not name.strip():
            ModelError.raise_error(
                err.KB_INVALID_PROPERTY_NAME_ID,
                message='Invalid property name.',
                name=name,
            )

        # The caller must pass string, number, or boolean. Nothing else.
        if value_type not in PROPERTY_VALUE_TYPES:
            ModelError.raise_error(
                err.KB_INVALID_PROPERTY_TYPE_ID,
                message='Invalid property value type.',
                value_type=value_type,
            )

        # The value must match the declared type, with no cross-type coercion.
        if not cls.value_matches(value, value_type):
            ModelError.raise_error(
                err.KB_INVALID_PROPERTY_VALUE_ID,
                message='Property value does not match the declared type.',
                value_type=value_type,
            )

    # * method: filter_rejection
    @classmethod
    def filter_rejection(cls,
            name: Any,
            value: Any,
            value_type: Any,
        ) -> None:
        '''
        Raise ModelError for an incomplete or invalid property filter.

        All three arguments omitted (``None``) is no filter. ``False``, ``0``,
        and ``''`` are real values, not omissions. If any argument is set, all
        three are required, and the same type rules as a write apply.

        :param name: The filter name, or None when omitted.
        :type name: Any
        :param value: The filter value, or None when omitted.
        :type value: Any
        :param value_type: The filter type, or None when omitted.
        :type value_type: Any
        :return: None
        :rtype: None
        '''

        # Omission is None on every argument, not a false or empty value.
        supplied = (
            name is not None,
            value is not None,
            value_type is not None,
        )
        if not any(supplied):
            return

        # A partial triple is not a filter. There is no name-only match.
        if not all(supplied):
            ModelError.raise_error(
                err.KB_INVALID_PROPERTY_FILTER_ID,
                message='A property filter requires name, value, and value type.',
                name=name,
                value_type=value_type,
            )

        # A complete triple uses the write rules.
        cls.rejection(name, value, value_type)

# ** model: document
class Document(DomainObject):
    '''
    A knowledge base document.

    Documents are the primary content objects in the knowledge base,
    composed of ordered sections and optionally classified by category,
    sourced from a template, and placed within a folder. A property bag
    holds caller-named typed values that are not header columns.
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

    # * attribute: properties
    properties: List[DocumentProperty] = Field(
        default_factory=list,
        description='Property bag sorted by name when loaded. Empty is not a claim that the bag is empty unless it was loaded.',
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
