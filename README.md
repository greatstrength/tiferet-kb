# tiferet-kb

A Knowledge Base extension for the [Tiferet](https://github.com/greatstrength/tiferet) framework with HDF5-backed storage via [tiferet-h5](https://github.com/greatstrength/tiferet-h5).

## Overview

**tiferet-kb** provides a Domain-Driven Design (DDD) layer for building knowledge base applications — managing documents, sections, categories, templates, and folder hierarchies. Built on the Tiferet framework and backed by HDF5 for efficient structured storage.

## Installation

```bash
pip install tiferet-kb
```

**Requirements:** Python ≥ 3.10, tiferet ≥ 2.0.0b3, tiferet-h5 ≥ 0.1.0

## Quick Start

```python
from tiferet_kb.repos.category import CategoryH5Repository
from tiferet_kb.repos.document import DocumentH5Repository
from tiferet_kb.mappers import CategoryAggregate, DocumentAggregate, DocumentSectionAggregate

# Initialize repositories pointing to a single HDF5 file.
category_repo = CategoryH5Repository(h5_file='kb.h5')
doc_repo = DocumentH5Repository(h5_file='kb.h5')

# Create a category.
category = CategoryAggregate(id='meeting-notes', name='Meeting Notes', icon='📝')
category_repo.save(category)

# Create a document.
doc = DocumentAggregate(title='Sprint Retro', category_id='meeting-notes')
doc_repo.save(doc)

# Add a section.
section = DocumentSectionAggregate(
    document_id=doc.id, title='What went well',
    content_type='markdown', content='- Shipped on time', position=0,
)
doc_repo.save_section(section)

# Retrieve the document with sections.
result = doc_repo.get(doc.id)
print(result.title)              # 'Sprint Retro'
print(result.sections[0].title)  # 'What went well'
```

## API Reference

### Domain Objects

All domain objects extend `tiferet.domain.DomainObject` (Pydantic v2, read-only).

#### Category

Lightweight metadata for classifying documents.

```python
from tiferet_kb import Category

category = Category(
    id='design-docs',          # slug-style identifier
    name='Design Docs',
    description='Architecture and design documents',
    icon='📐',
    color='#8B5CF6',
)
```

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `str` | yes | Slug-style identifier |
| `name` | `str` | yes | Display name |
| `description` | `str \| None` | no | Optional description |
| `icon` | `str \| None` | no | Emoji or icon identifier |
| `color` | `str \| None` | no | Hex color string |

#### Document

Primary content object, composed of ordered sections.

```python
from tiferet_kb import Document

doc = Document(title='Sprint Retro')  # id, status, timestamps auto-generated
```

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `str` | auto | UUID (auto-generated if absent) |
| `title` | `str` | yes | Document title |
| `category_id` | `str \| None` | no | FK to Category |
| `template_id` | `str \| None` | no | FK to Template |
| `folder_id` | `str \| None` | no | FK to Folder |
| `status` | `str` | auto | `draft`, `published`, or `archived` (default: `draft`) |
| `created_at` | `str` | auto | ISO 8601 timestamp |
| `updated_at` | `str` | auto | ISO 8601 timestamp |
| `sections` | `List[DocumentSection]` | no | Populated by service layer |

**Methods:** `get_section(position)`, `section_count()`

#### DocumentSection

A content block within a document.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `str` | auto | UUID |
| `document_id` | `str` | yes | Parent document UUID |
| `title` | `str` | yes | Section heading |
| `content_type` | `str` | yes | `text`, `markdown`, `code`, `table`, `image` |
| `content` | `str` | no | Raw content (default: `''`) |
| `position` | `int` | yes | Zero-based ordering |
| `created_at` | `str` | auto | ISO 8601 timestamp |
| `updated_at` | `str` | auto | ISO 8601 timestamp |

### Domain Events

All events use the standard `DomainEvent.handle()` invocation pattern:

```python
from tiferet.events import DomainEvent
from tiferet_kb.events import AddDocument

result = DomainEvent.handle(
    AddDocument,
    dependencies={'document_service': doc_repo},
    title='My Document',
    category_id='meeting-notes',
)
```

#### Category Events

| Event | Required Params | Description |
|---|---|---|
| `AddCategory` | `id`, `name` | Create a new category |
| `GetCategory` | `id` | Retrieve by ID |
| `ListCategories` | — | List all categories |
| `UpdateCategory` | `id`, `attribute` | Update `name`, `description`, `icon`, or `color` |
| `RemoveCategory` | `id` | Delete (idempotent) |

#### Document Events

| Event | Required Params | Description |
|---|---|---|
| `AddDocument` | `title` | Create a new document (UUID auto-generated) |
| `GetDocument` | `id` | Retrieve with sections |
| `ListDocuments` | — | List with optional `folder_id`, `category_id`, `status` filters |
| `UpdateDocument` | `id`, `attribute` | Update `title`, `status`, `category_id`, or `folder_id` |
| `RemoveDocument` | `id` | Delete with cascading section removal |

#### Section Events

| Event | Required Params | Description |
|---|---|---|
| `AddDocumentSection` | `document_id`, `title`, `content_type` | Add a section (auto-appends or explicit position) |
| `UpdateDocumentSection` | `id`, `attribute` + `document_id` | Update `title`, `content`, or `content_type` |
| `RemoveDocumentSection` | `id` | Delete a section (idempotent) |
| `ReorderDocumentSections` | `document_id`, `section_ids` | Reorder sections by providing ID list |

#### Template Events

| Event | Required Params | Description |
|---|---|---|
| `AddTemplate` | `name` | Create a template (optionally with initial `sections` list) |
| `GetTemplate` | `id` | Retrieve with sections |
| `ListTemplates` | — | List with optional `category_id` filter |
| `UpdateTemplate` | `id`, `attribute` | Update `name`, `description`, or `category_id` |
| `RemoveTemplate` | `id` | Delete with cascading section removal |
| `ApplyTemplate` | `template_id`, `title` | Create a document from a template (stamps sections) |

### Repositories

Repositories implement Service interfaces and use `tiferet_h5.H5Repository` for HDF5 access.

#### CategoryH5Repository

Stores categories as **node attributes** on HDF5 groups at `/kb/categories/<id>`.

```python
from tiferet_kb.repos.category import CategoryH5Repository

repo = CategoryH5Repository(h5_file='kb.h5')
repo.save(category)           # Create or update
repo.get('meeting-notes')     # Retrieve
repo.list()                   # List all
repo.exists('meeting-notes')  # Check existence
repo.delete('meeting-notes')  # Remove (idempotent)
```

#### DocumentH5Repository

Stores documents as **table rows** in `/kb/documents/documents` and sections in `/kb/documents/document_sections`.

```python
from tiferet_kb.repos.document import DocumentH5Repository

repo = DocumentH5Repository(h5_file='kb.h5')
repo.save(document)                              # Upsert document header
repo.get('doc-id')                               # Retrieve with sections joined
repo.list(status='draft', category_id='notes')   # Filtered listing
repo.save_section(section)                       # Upsert a section
repo.get_sections('doc-id')                      # List sections by position
repo.reorder_sections('doc-id', ['s2', 's1'])    # Reorder sections
repo.delete_section('section-id')                # Remove a section
repo.delete('doc-id')                            # Cascade delete doc + sections
```

### HDF5 Storage Layout

```
/kb/
├── categories/
│   └── <category_id>/          ← group node, attrs: name, description, icon, color
├── documents/
│   ├── documents               ← table: id, title, category_id, status, ...
│   └── document_sections       ← table: id, document_id, title, content, position, ...
└── templates/
    ├── templates               ← table: id, name, description, category_id, ...
    └── template_sections       ← table: id, template_id, title, default_content, position, ...
```

## Architecture

```
tiferet_kb/
├── assets/         Error code constants
├── domain/         DomainObject subclasses (Category, Document, DocumentSection)
├── interfaces/     Service ABC contracts (CategoryService, DocumentService)
├── mappers/        Aggregate + NodeObject + TableObject mappers
│   └── tests/      Harness-based tests (AggregateTestBase, NodeObjectTestBase)
├── events/         DomainEvent subclasses (CRUD operations)
└── repos/          H5Repository implementations
```

## Development

```bash
# Create virtual environment and install with test deps
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"

# Run tests
pytest --verbose
```

## Documentation

Guide docs are available in `docs/guides/`:
- [Domain Objects](docs/guides/domain.md)
- [Mappers](docs/guides/mappers.md)
- [Events](docs/guides/events.md)
- [Repositories](docs/guides/repos.md)

## License

BSD 3-Clause License. See [LICENSE](LICENSE) for details.
