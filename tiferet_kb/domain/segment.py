"""tiferet_kb Segment Domain"""

# *** imports

# ** core
from typing import Any, List, Optional
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject

# *** models

# ** model: text_segment
class TextSegment(DomainObject):
    '''
    A contiguous run of text sharing a single formatting style.

    Text segments are the atomic units of rich-text content. Each segment
    carries its text, a format type (plain, bold, italic, strikethrough,
    code, link), and an optional link URL.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this segment.',
    )

    # * attribute: position
    position: int = Field(
        ...,
        description='Zero-based ordering position within the paragraph.',
    )

    # * attribute: text
    text: str = Field(
        ...,
        description='The raw text content of this segment.',
    )

    # * attribute: format_type
    format_type: str = Field(
        default='plain',
        description='Formatting style: plain, bold, italic, strikethrough, code, link.',
    )

    # * attribute: link_url
    link_url: Optional[str] = Field(
        default=None,
        description='URL target when format_type is link.',
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


# ** model: paragraph
class Paragraph(DomainObject):
    '''
    A block-level content unit within a section, composed of text segments.

    Paragraphs represent logical blocks of content (normal text, quotations,
    code blocks, list items) and contain an ordered list of TextSegment
    objects that carry the inline formatting.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this paragraph.',
    )

    # * attribute: section_id
    section_id: str = Field(
        ...,
        description='UUID of the parent section.',
    )

    # * attribute: position
    position: int = Field(
        ...,
        description='Zero-based ordering position within the section.',
    )

    # * attribute: block_type
    block_type: str = Field(
        default='normal',
        description='Block style: normal, quote, code_block, list_item.',
    )

    # * attribute: segments
    segments: List[TextSegment] = Field(
        default_factory=list,
        description='Ordered list of text segments.',
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
