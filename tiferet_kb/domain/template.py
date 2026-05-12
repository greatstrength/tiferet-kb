"""tiferet_kb Template Domain"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any, List, Optional
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject

# *** models

# ** model: template_section
class TemplateSection(DomainObject):
    '''
    A section blueprint within a knowledge base template.

    Defines the default heading, content type, and pre-filled content
    that will be stamped into a new document when the template is applied.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this template section.',
    )

    # * attribute: template_id
    template_id: str = Field(
        ...,
        description='UUID of the parent template.',
    )

    # * attribute: title
    title: str = Field(
        ...,
        description='Default section heading.',
    )

    # * attribute: content_type
    content_type: str = Field(
        ...,
        description='Default content type: text, markdown, code, table, or image.',
    )

    # * attribute: default_content
    default_content: str = Field(
        default='',
        description='Pre-filled content for the section.',
    )

    # * attribute: position
    position: int = Field(
        ...,
        description='Zero-based ordering position within the template.',
    )

    # * method: _derive_defaults (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_defaults(cls, data: Any) -> Any:
        '''
        Derive default id when absent.

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

        # Return the augmented data.
        return data


# ** model: template
class Template(DomainObject):
    '''
    A knowledge base template for creating documents with pre-defined sections.

    Templates define a reusable structure of section blueprints that are
    stamped into new documents via the ApplyTemplate event.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this template.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='Template name.',
    )

    # * attribute: description
    description: Optional[str] = Field(
        default=None,
        description='Optional template description.',
    )

    # * attribute: category_id
    category_id: Optional[str] = Field(
        default=None,
        description='Suggested category for documents created from this template.',
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
    sections: List[TemplateSection] = Field(
        default_factory=list,
        description='Ordered list of template section blueprints, populated by the service layer.',
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

    # * method: get_section
    def get_section(self, position: int) -> Optional[TemplateSection]:
        '''
        Get the template section at the given position.

        :param position: The index of the section to retrieve.
        :type position: int
        :return: The TemplateSection at the position, or None.
        :rtype: TemplateSection | None
        '''

        # Attempt to retrieve the section, returning None if out of range.
        try:
            return self.sections[position]
        except (IndexError, TypeError):
            return None
