"""
tiferet_kb Example — Knowledge Base Demo

Demonstrates the core KB workflow through KB(path):

  1. Create a category
  2. Import a markdown document (H1-delimited sections)
  3. List documents
  4. Export the document back to markdown

Run:
    python examples/kb_demo.py
    python examples/kb_demo.py /path/to/kb.h5
"""

# *** imports

# ** core
import sys
import tempfile
from pathlib import Path

# ** app
from tiferet_kb import KB

# *** functions

# ** function: resolve_path
def resolve_path() -> str:
    '''
    Return the caller path, or create one temporary path.

    :return: A filesystem path for the knowledge-base file.
    :rtype: str
    '''

    # Accept a path from the command line when one is given.
    if len(sys.argv) > 1:
        return sys.argv[1]

    # Otherwise create a temporary directory and name the file there.
    directory = tempfile.mkdtemp(prefix='tiferet-kb-demo-')
    return str(Path(directory) / 'kb.h5')

# *** demo

# The existing H1 sample. The script does not choose a path inside KB.
SAMPLE_MARKDOWN = """\
# Getting Started

Welcome to the knowledge base. This guide covers the basics.

## Prerequisites

- Python 3.10+
- tiferet >= 2.0.0b3
- tiferet-kb >= 1.0.0b3

## Installation

Install via pip:

```
pip install tiferet-kb
```

# Working with Documents

Documents are the primary content objects in the knowledge base.

Each document is composed of ordered **sections**, and each section
contains structured *paragraphs* with rich-text segments.

# Markdown Convention

Every markdown document **must start with an H1 heading** (`# Title`).

Each H1 heading begins a new section. Sub-headings (`##`, `###`, etc.)
and all other content belong to the current section.

This convention keeps parsing simple and unambiguous — ideal for
agent-generated content.
"""

print('=== tiferet_kb Demo ===\n')

path = resolve_path()
session = KB(path)
print(f'File: {path}\n')

# --- Step 1: Create a category ---
print('1. Creating category "guides"...')
category = session.run(
    'category.add',
    data={
        'id': 'guides',
        'name': 'Guides',
        'description': 'How-to guides and tutorials',
        'icon': '📖',
    },
)
print(f'   Created: {category.id} — {category.name}\n')

# --- Step 2: Import a markdown document ---
print('2. Importing markdown document...')
document = session.run(
    'markdown.import',
    data={
        'content': SAMPLE_MARKDOWN,
        'category_id': 'guides',
    },
)
print(f'   Document: "{document.title}" (id={document.id})')
print(f'   Sections: {len(document.sections)}')
for sec in document.sections:
    para_count = len(sec.paragraphs)
    print(f'     [{sec.position}] {sec.title} ({para_count} paragraphs)')
print()

# --- Step 3: List documents ---
print('3. Listing documents...')
docs = session.run('document.list', data={})
for doc in docs:
    print(f'   - {doc.title} (status={doc.status}, sections={len(doc.sections)})')
print()

# --- Step 4: Export back to markdown ---
print('4. Exporting document to markdown...')
exported_md = session.run(
    'markdown.export',
    data={'id': document.id},
)

print('--- Exported Markdown ---')
print(exported_md)
print('--- End ---')
print('\nDemo complete.')
