"""tiferet_kb Folder Domain"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject

# *** models

# ** model: folder
class Folder(DomainObject):
    '''
    A knowledge base folder for organizing documents in a hierarchy.

    Folders are identified by UUID and support nesting via ``parent_id``.
    The ``path`` field stores a materialized path string (e.g.
    ``'/projects/design'``) for efficient prefix-based queries.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this folder.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='Folder display name.',
    )

    # * attribute: parent_id
    parent_id: Optional[str] = Field(
        default=None,
        description='UUID of the parent folder, or None for root-level folders.',
    )

    # * attribute: path
    path: str = Field(
        ...,
        description='Materialized path string, e.g. "/projects/design".',
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
        Derive default values for id, path, and created_at when absent.

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

        # Derive path from name if not provided.
        if not data.get('path') and data.get('name'):
            data['path'] = f'/{data["name"]}'

        # Set created_at if not provided.
        if not data.get('created_at'):
            data['created_at'] = datetime.now(timezone.utc).isoformat()

        # Return the augmented data.
        return data
