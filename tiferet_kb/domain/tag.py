"""tiferet_kb Tag Domain"""

# *** imports

# ** core
from typing import Optional

# ** infra
from pydantic import Field

# ** app
from tiferet.domain import DomainObject

# *** models

# ** model: tag
class Tag(DomainObject):
    '''
    A many-to-many label a document can carry beside its one optional category.

    A tag is a shared catalog entry the caller names. Documents are not copied
    into it, and it does not replace ``category_id``.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='Caller-supplied slug-style identifier for the tag.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='Human-readable display name of the tag.',
    )

    # * attribute: color
    color: Optional[str] = Field(
        default=None,
        description='Optional color string. Absent as None. Not a validated palette.',
    )
