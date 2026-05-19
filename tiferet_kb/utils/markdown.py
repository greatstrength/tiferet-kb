"""tiferet_kb Markdown Parser Utility"""

# *** imports

# ** core
import re
from typing import List
from uuid import uuid4

# ** app
from ..domain.segment import TextSegment, Paragraph

# *** constants

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
def parse_paragraph_to_segments(text: str) -> List[TextSegment]:
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
def reassemble_paragraph(segments: List[TextSegment]) -> str:
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


# ** function: split_markdown_sections
def split_markdown_sections(content: str) -> List[dict]:
    '''
    Split a markdown document into sections delimited by H1 headings.

    Convention: every document must start with an ``# H1`` heading.
    Each H1 line begins a new section whose title is the heading text
    and whose content is everything between this H1 and the next (or EOF).

    :param content: The full markdown document string.
    :type content: str
    :return: Ordered list of dicts with ``title`` and ``content`` keys.
    :rtype: List[dict]
    :raises ValueError: If the content does not start with an H1 heading.
    '''

    if not content or not content.strip():
        return []

    lines = content.strip().split('\n')

    # Validate that the document starts with an H1 heading.
    if not lines[0].startswith('# '):
        raise ValueError(
            'Markdown document must start with an H1 heading ("# Title"). '
            'Each H1 heading delimits a new section.'
        )

    sections: List[dict] = []
    current_title: str | None = None
    current_lines: List[str] = []

    for line in lines:

        # Detect H1 heading (but not ## or deeper).
        if line.startswith('# ') and not line.startswith('## '):

            # Flush the previous section if one exists.
            if current_title is not None:
                sections.append({
                    'title': current_title,
                    'content': '\n'.join(current_lines).strip(),
                })

            # Start a new section.
            current_title = line[2:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Flush the final section.
    if current_title is not None:
        sections.append({
            'title': current_title,
            'content': '\n'.join(current_lines).strip(),
        })

    return sections


# ** function: join_markdown_sections
def join_markdown_sections(sections) -> str:
    '''
    Reconstruct a markdown document from ordered sections.

    Each section is emitted as ``# {title}`` followed by its content,
    separated by double newlines.

    :param sections: Ordered iterable of objects with ``title`` and
        ``content`` attributes (or dicts with those keys).
    :type sections: Iterable
    :return: The assembled markdown string.
    :rtype: str
    '''

    parts: List[str] = []

    for section in sections:

        # Support both dict and object access.
        if isinstance(section, dict):
            title = section['title']
            content = section.get('content', '')
        else:
            title = section.title
            content = getattr(section, 'content', '')

        # Build the section markdown.
        block = f'# {title}'
        if content:
            block += f'\n\n{content}'
        parts.append(block)

    return '\n\n'.join(parts) + '\n' if parts else ''


# ** function: parse_content_to_paragraphs
def parse_content_to_paragraphs(content: str, section_id: str) -> List[Paragraph]:
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
