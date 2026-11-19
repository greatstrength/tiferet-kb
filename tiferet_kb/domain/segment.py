"""tiferet_kb Segment Domain"""

# *** imports

# ** core
import re
from typing import Any, List, Optional
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject

# *** constants

# ** constant: inline_pattern
# Regex pattern matching inline markdown tokens in priority order.
# Order matters: **bold** must be checked before *italic*.
_INLINE_PATTERN = re.compile(
    r'(?P<bold>\*\*(?P<bold_text>.+?)\*\*)'
    r'|(?P<italic>\*(?P<italic_text>.+?)\*)'
    r'|(?P<strike>~~(?P<strike_text>.+?)~~)'
    r'|(?P<code>`(?P<code_text>.+?)`)'
    r'|(?P<link>\[(?P<link_text>.+?)\]\((?P<link_url>.+?)\))'
)

# *** functions

# ** function: parse_paragraph_to_segments
def parse_paragraph_to_segments(text: str) -> List['TextSegment']:
    '''
    Tokenize a markdown paragraph string into ordered TextSegment objects.

    Supported inline formats:
      **bold**, *italic*, ~~strikethrough~~, `code`, [text](url)
    Everything else is emitted as plain text.

    :param text: The raw markdown paragraph text.
    :type text: str
    :return: Ordered list of TextSegment objects.
    :rtype: List[TextSegment]
    '''

    segments: List[TextSegment] = []
    pos = 0
    cursor = 0

    for match in _INLINE_PATTERN.finditer(text):
        start, end = match.start(), match.end()

        # Emit plain text before this match.
        if start > cursor:
            plain = text[cursor:start]
            if plain:
                segments.append(TextSegment(
                    position=pos, text=plain, format_type='plain',
                ))
                pos += 1

        # Determine which group matched.
        if match.group('bold'):
            segments.append(TextSegment(
                position=pos, text=match.group('bold_text'), format_type='bold',
            ))
        elif match.group('italic'):
            segments.append(TextSegment(
                position=pos, text=match.group('italic_text'), format_type='italic',
            ))
        elif match.group('strike'):
            segments.append(TextSegment(
                position=pos, text=match.group('strike_text'), format_type='strikethrough',
            ))
        elif match.group('code'):
            segments.append(TextSegment(
                position=pos, text=match.group('code_text'), format_type='code',
            ))
        elif match.group('link'):
            segments.append(TextSegment(
                position=pos,
                text=match.group('link_text'),
                format_type='link',
                link_url=match.group('link_url'),
            ))

        pos += 1
        cursor = end

    # Emit trailing plain text.
    if cursor < len(text):
        trailing = text[cursor:]
        if trailing:
            segments.append(TextSegment(
                position=pos, text=trailing, format_type='plain',
            ))

    return segments

# ** function: reassemble_paragraph
def reassemble_paragraph(segments: List['TextSegment']) -> str:
    '''
    Reassemble a list of TextSegments back into a markdown string.

    :param segments: Ordered list of TextSegment objects.
    :type segments: List[TextSegment]
    :return: The reassembled markdown string.
    :rtype: str
    '''

    parts: List[str] = []

    for seg in sorted(segments, key=lambda s: s.position):
        if seg.format_type == 'plain':
            parts.append(seg.text)
        elif seg.format_type == 'bold':
            parts.append(f'**{seg.text}**')
        elif seg.format_type == 'italic':
            parts.append(f'*{seg.text}*')
        elif seg.format_type == 'strikethrough':
            parts.append(f'~~{seg.text}~~')
        elif seg.format_type == 'code':
            parts.append(f'`{seg.text}`')
        elif seg.format_type == 'link':
            parts.append(f'[{seg.text}]({seg.link_url})')
        else:
            parts.append(seg.text)

    return ''.join(parts)

# ** function: parse_content_to_paragraphs
def parse_content_to_paragraphs(content: str, section_id: str) -> List['Paragraph']:
    '''
    Split a markdown content string into Paragraph objects with parsed segments.

    Block-level rules:
      - Split on double-newlines to separate paragraphs.
      - Lines starting with ``>`` are detected as ``quote`` block type
        (the ``>`` prefix is stripped before inline parsing).
      - Blocks enclosed in triple backticks are detected as ``code_block``
        (content is kept as a single plain segment).
      - Everything else is ``normal``.

    :param content: The full markdown content string.
    :type content: str
    :param section_id: The parent section UUID.
    :type section_id: str
    :return: Ordered list of Paragraph objects.
    :rtype: List[Paragraph]
    '''

    if not content or not content.strip():
        return []

    # Split on double-newlines to get raw blocks.
    raw_blocks = re.split(r'\n\n+', content.strip())
    paragraphs: List[Paragraph] = []

    for position, block in enumerate(raw_blocks):
        block = block.strip()
        if not block:
            continue

        # Detect code block (triple backtick fence).
        if block.startswith('```') and block.endswith('```'):
            # Strip the fences and keep content as a single plain segment.
            code_content = block[3:]
            if code_content.endswith('```'):
                code_content = code_content[:-3]
            # Strip optional language identifier on the first line.
            lines = code_content.split('\n', 1)
            if len(lines) > 1:
                code_content = lines[1]
            else:
                code_content = lines[0]

            paragraphs.append(Paragraph(
                section_id=section_id,
                position=position,
                block_type='code_block',
                segments=[TextSegment(
                    position=0, text=code_content.strip(), format_type='plain',
                )],
            ))
            continue

        # Detect quote block (lines starting with >).
        if block.startswith('>'):
            # Strip > prefix from each line.
            lines = block.split('\n')
            cleaned = '\n'.join(
                line.lstrip('>').lstrip() for line in lines
            )
            segments = parse_paragraph_to_segments(cleaned)
            paragraphs.append(Paragraph(
                section_id=section_id,
                position=position,
                block_type='quote',
                segments=segments,
            ))
            continue

        # Default: normal paragraph.
        segments = parse_paragraph_to_segments(block)
        paragraphs.append(Paragraph(
            section_id=section_id,
            position=position,
            block_type='normal',
            segments=segments,
        ))

    return paragraphs

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
