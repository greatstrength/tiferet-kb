"""tiferet_kb Document Link Domain"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject

from ..assets.core import (
    DOCUMENT_LINK_REFERENCES,
    DOCUMENT_LINK_RELATED_TO,
    DOCUMENT_LINK_SUPERSEDES,
)

# *** models

# ** model: document_link
class DocumentLink(DomainObject):
    '''
    A directional pointer from one document to another in the same file.

    The pointer is a stored relationship: the source cites, replaces, or
    sits beside the target. It is not a category, a folder, a template
    stamp, or a formatted passage.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this link.',
    )

    # * attribute: source_id
    source_id: str = Field(
        ...,
        description='Identifier of the document the link starts from.',
    )

    # * attribute: target_id
    target_id: str = Field(
        ...,
        description='Identifier of the document the link points at.',
    )

    # * attribute: link_type
    link_type: Literal[
        DOCUMENT_LINK_REFERENCES,
        DOCUMENT_LINK_SUPERSEDES,
        DOCUMENT_LINK_RELATED_TO,
    ] = Field(
        ...,
        description='Documented relationship: references, supersedes, or related_to.',
    )

    # * attribute: created_at
    created_at: str = Field(
        ...,
        description='ISO 8601 creation timestamp.',
    )

    # * method: _derive_defaults (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_defaults(cls, data: Any) -> Any:
        '''
        Derive id and created_at when absent, and strip the link type.

        Stripping the ends keeps a trailing space from missing the
        documented name. Case is left as given.

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

        # Strip the type when the caller passed a string. Do not fold case.
        link_type = data.get('link_type')
        if isinstance(link_type, str):
            data['link_type'] = link_type.strip()

        # Set the timestamp if not provided. The caller does not pass it on add.
        if not data.get('created_at'):
            data['created_at'] = datetime.now(timezone.utc).isoformat()

        # Return the augmented data.
        return data
