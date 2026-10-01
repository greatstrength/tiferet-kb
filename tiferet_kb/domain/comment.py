"""tiferet_kb Section Comment Domain"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject

# *** constants

# ** constant: author_max_length
AUTHOR_MAX_LENGTH = 512

# ** constant: text_max_length
TEXT_MAX_LENGTH = 8192

# *** models

# ** model: section_comment
class SectionComment(DomainObject):
    '''
    A plain-text note on one section, kept beside the section rather than inside it.

    The note is not a passage and not a field on the section. A passage rewrite
    therefore does not erase it, and exporting the section does not include it.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this comment.',
    )

    # * attribute: document_id
    document_id: str = Field(
        ...,
        description='UUID of the document that owns the section.',
    )

    # * attribute: section_id
    section_id: str = Field(
        ...,
        description='UUID of the section this note is attached to.',
    )

    # * attribute: author
    author: str = Field(
        ...,
        description='Caller-supplied author string. Not an account.',
    )

    # * attribute: text
    text: str = Field(
        ...,
        description='Plain-text note. Markdown characters stay characters.',
    )

    # * attribute: parent_id
    parent_id: Optional[str] = Field(
        default=None,
        description='Optional identifier of the comment this note replies to.',
    )

    # * attribute: created_at
    created_at: str = Field(
        ...,
        description='ISO 8601 creation timestamp. There is no update timestamp.',
    )

    # * method: _derive_defaults (model validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_defaults(cls, data: Any) -> Any:
        '''
        Derive id and created_at when the caller omits them.

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

        # Set the creation timestamp if not provided. There is no updated_at.
        if not data.get('created_at'):
            data['created_at'] = datetime.now(timezone.utc).isoformat()

        # Return the augmented data.
        return data
