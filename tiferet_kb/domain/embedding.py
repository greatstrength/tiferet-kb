"""tiferet_kb Embedding Domain"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject

# *** models

# ** model: embedding_record
class EmbeddingRecord(DomainObject):
    '''
    A lightweight value object tracking embedding metadata for a document section.

    The actual embedding vector is stored as a contiguous HDF5 array;
    this record captures the section association, model provenance,
    dimensionality, and creation timestamp.
    '''

    # * attribute: section_id
    section_id: str = Field(
        ...,
        description='UUID of the embedded document section.',
    )

    # * attribute: model_name
    model_name: str = Field(
        ...,
        description='Name of the embedding model (e.g. "text-embedding-3-small").',
    )

    # * attribute: dimensions
    dimensions: int = Field(
        ...,
        description='Dimensionality of the embedding vector (e.g. 1536).',
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
        Derive default values for created_at when absent.

        :param data: The raw input data.
        :type data: Any
        :return: The augmented input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Set timestamp if not provided.
        if not data.get('created_at'):
            data['created_at'] = datetime.now(timezone.utc).isoformat()

        # Return the augmented data.
        return data
