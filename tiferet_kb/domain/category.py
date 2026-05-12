"""tiferet_kb Category Domain"""

# *** imports

# ** core
from typing import Optional

# ** infra
from pydantic import Field

# ** app
from tiferet.domain import DomainObject

# *** models

# ** model: category
class Category(DomainObject):
    '''
    A knowledge base category used to classify documents.

    Categories are lightweight metadata objects identified by a slug-style
    string (e.g. ``'meeting-notes'``, ``'design-docs'``).
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='Slug-style unique identifier for the category.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='Human-readable display name of the category.',
    )

    # * attribute: description
    description: Optional[str] = Field(
        default=None,
        description='Optional description of the category.',
    )

    # * attribute: icon
    icon: Optional[str] = Field(
        default=None,
        description='Optional emoji or icon identifier for the category.',
    )

    # * attribute: color
    color: Optional[str] = Field(
        default=None,
        description='Optional hex color string for the category (e.g. "#3B82F6").',
    )
