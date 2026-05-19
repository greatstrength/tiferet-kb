"""
tiferet_kb Example — Knowledge Base Demo

Demonstrates the core KB workflow using DomainEvent.handle() with mock
services.  This script exercises:

  1. Create a category
  2. Import a markdown document (H1-delimited sections)
  3. List documents
  4. Export the document back to markdown

Run:
    python examples/kb_demo.py
"""

# *** imports

# ** core
from unittest import mock

# ** app
from tiferet.events import DomainEvent

from tiferet_kb.interfaces import CategoryService, DocumentService
from tiferet_kb.events import (
    AddCategory,
    ListCategories,
    ImportMarkdownDocument,
    ExportDocumentMarkdown,
    ListDocuments,
)

# *** setup

# Mock services — replace with real H5-backed repos for production use.
mock_category_service = mock.Mock(spec=CategoryService)
mock_category_service.exists.return_value = False
mock_category_service.list.return_value = []

mock_document_service = mock.Mock(spec=DocumentService)
mock_document_service.exists.return_value = False
mock_document_service.list.return_value = []

# *** demo

print('=== tiferet_kb Demo ===\n')

# --- Step 1: Create a category ---
print('1. Creating category "guides"...')
category = DomainEvent.handle(
    AddCategory,
    dependencies={'category_service': mock_category_service},
    id='guides',
    name='Guides',
    description='How-to guides and tutorials',
    icon='📖',
)
print(f'   Created: {category.id} — {category.name}\n')

# --- Step 2: Import a markdown document ---
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

print('2. Importing markdown document...')
document = DomainEvent.handle(
    ImportMarkdownDocument,
    dependencies={'document_service': mock_document_service},
    content=SAMPLE_MARKDOWN,
    category_id='guides',
)
print(f'   Document: "{document.title}" (id={document.id})')
print(f'   Sections: {len(document.sections)}')
for sec in document.sections:
    para_count = len(sec.paragraphs)
    print(f'     [{sec.position}] {sec.title} ({para_count} paragraphs)')
print()

# --- Step 3: List documents ---
# Wire mock to return the created document for listing.
mock_document_service.list.return_value = [document]

print('3. Listing documents...')
docs = DomainEvent.handle(
    ListDocuments,
    dependencies={'document_service': mock_document_service},
)
for doc in docs:
    print(f'   - {doc.title} (status={doc.status}, sections={len(doc.sections)})')
print()

# --- Step 4: Export back to markdown ---
# Wire mock to return the full document for export.
mock_document_service.get.return_value = document

print('4. Exporting document to markdown...')
exported_md = DomainEvent.handle(
    ExportDocumentMarkdown,
    dependencies={'document_service': mock_document_service},
    id=document.id,
)

print('--- Exported Markdown ---')
print(exported_md)
print('--- End ---')
print('\nDemo complete.')
