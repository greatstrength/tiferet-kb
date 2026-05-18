# tiferet-kb Domain Objects

**Package:** `tiferet_kb.domain`

## Overview

The domain layer defines `DomainObject` subclasses that capture knowledge base structural concepts as first-class Tiferet models.  These objects are read-only at this layer — mutation logic belongs in Aggregate subclasses in the mappers layer.

All classes extend `tiferet.domain.DomainObject` (backed by Pydantic v2).

---

## Category

**Module:** `tiferet_kb.domain.category`

Represents a knowledge base category used to classify documents.  Categories are lightweight metadata objects identified by a slug-style string (e.g. `'meeting-notes'`, `'design-docs'`).

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `str` | yes | Slug-style unique identifier (e.g. `'meeting-notes'`). |
| `name` | `str` | yes | Human-readable display name. |
| `description` | `str \| None` | no | Optional description of the category. |
| `icon` | `str \| None` | no | Optional emoji or icon identifier. |
| `color` | `str \| None` | no | Optional hex color string (e.g. `'#3B82F6'`). |

### Usage

```python
from tiferet_kb import Category

category = Category(
    id='meeting-notes',
    name='Meeting Notes',
    description='Notes from team meetings',
    icon='📝',
    color='#3B82F6',
)
```

### HDF5 Storage

Categories are stored as **node attributes** on HDF5 group nodes at `/kb/categories/<id>`.  The `id` field is encoded as the group name itself and is excluded from the serialized attributes — only `name`, `description`, `icon`, and `color` are written as `_v_attrs` entries.

This design is appropriate because categories are lightweight, infrequently changing metadata with a small number of scalar fields — the natural fit for HDF5 node attributes rather than table rows.

---

## Document

**Module:** `tiferet_kb.domain.document`

The primary content object in the knowledge base.  Documents are composed of ordered sections and optionally classified by category, sourced from a template, and placed within a folder.

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `str` | auto | UUID string (auto-generated if absent). |
| `title` | `str` | yes | Document title. |
| `category_id` | `str \| None` | no | Optional category identifier. |
| `template_id` | `str \| None` | no | Optional template used to create this document. |
| `folder_id` | `str \| None` | no | Optional folder identifier. |
| `status` | `str` | no | `draft` (default), `published`, or `archived`. |
| `created_at` | `str` | auto | ISO 8601 timestamp (auto-derived). |
| `updated_at` | `str` | auto | ISO 8601 timestamp (auto-derived). |
| `sections` | `List[DocumentSection]` | no | Ordered sections, populated by the service layer. |

### Methods

- **`get_section(position: int) -> DocumentSection | None`** — Retrieve section at the given index.
- **`section_count() -> int`** — Return the number of sections.

### Usage

```python
from tiferet_kb import Document

doc = Document(title='My Document', category_id='meeting-notes')
# id, created_at, updated_at are auto-generated
```

### HDF5 Storage

Documents are stored as **table rows** in `/kb/documents/documents` via `DocumentTableObject`.

---

## DocumentSection

**Module:** `tiferet_kb.domain.document`

A section within a document, holding a block of content with a specific type and an explicit ordering position.

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `str` | auto | UUID string (auto-generated if absent). |
| `document_id` | `str` | yes | UUID of the parent document. |
| `title` | `str` | yes | Section heading. |
| `content_type` | `str` | yes | `text`, `markdown`, `code`, `table`, or `image`. |
| `content` | `str` | no | Raw section content (default `''`). |
| `position` | `int` | yes | Zero-based ordering position. |
| `created_at` | `str` | auto | ISO 8601 timestamp. |
| `updated_at` | `str` | auto | ISO 8601 timestamp. |

### HDF5 Storage

Sections are stored as **table rows** in `/kb/documents/document_sections` via `DocumentSectionTableObject`.

---

## Template

**Module:** `tiferet_kb.domain.template`

A reusable structure of section blueprints for creating documents.  Templates define default headings, content types, and pre-filled content that are stamped into new documents via the `ApplyTemplate` event.

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `str` | auto | UUID string (auto-generated if absent). |
| `name` | `str` | yes | Template name. |
| `description` | `str \| None` | no | Optional description. |
| `category_id` | `str \| None` | no | Suggested category for documents created from this template. |
| `created_at` | `str` | auto | ISO 8601 timestamp. |
| `updated_at` | `str` | auto | ISO 8601 timestamp. |
| `sections` | `List[TemplateSection]` | no | Ordered section blueprints. |

### Methods

- **`get_section(position: int) -> TemplateSection | None`** — Retrieve section blueprint at the given index.

### HDF5 Storage

Templates are stored as **table rows** in `/kb/templates/templates` via `TemplateTableObject`.

---

## TemplateSection

**Module:** `tiferet_kb.domain.template`

A section blueprint within a template.

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `str` | auto | UUID string (auto-generated if absent). |
| `template_id` | `str` | yes | UUID of the parent template. |
| `title` | `str` | yes | Default section heading. |
| `content_type` | `str` | yes | Default content type. |
| `default_content` | `str` | no | Pre-filled content (default `''`). |
| `position` | `int` | yes | Zero-based ordering position. |

### HDF5 Storage

Template sections are stored as **table rows** in `/kb/templates/template_sections` via `TemplateSectionTableObject`.

---

## Folder

**Module:** `tiferet_kb.domain.folder`

A folder for organizing documents in a hierarchy.  Folders support nesting via `parent_id` and store a materialized path for efficient prefix-based queries.

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `str` | auto | UUID string (auto-generated if absent). |
| `name` | `str` | yes | Folder display name. |
| `parent_id` | `str \| None` | no | UUID of the parent folder, or `None` for root. |
| `path` | `str` | auto | Materialized path (auto-derived from name if absent). |
| `created_at` | `str` | auto | ISO 8601 timestamp. |

### HDF5 Storage

Folders are stored as **node attributes** on HDF5 group nodes at `/kb/folders/<id>`, similar to categories.

---

## EmbeddingRecord

**Module:** `tiferet_kb.domain.embedding`

A lightweight value object tracking embedding metadata for a document section.  The actual embedding vector is stored as a contiguous HDF5 array; this record captures the section association, model provenance, and dimensionality.

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `section_id` | `str` | yes | UUID of the embedded document section. |
| `model_name` | `str` | yes | Name of the embedding model. |
| `dimensions` | `int` | yes | Dimensionality of the embedding vector. |
| `created_at` | `str` | auto | ISO 8601 timestamp. |

---

## Import Reference

```python
from tiferet_kb import Category, Document, DocumentSection, Template, TemplateSection, Folder, EmbeddingRecord
# or
from tiferet_kb.domain import Category, Document, DocumentSection, Template, TemplateSection, Folder
from tiferet_kb.domain.embedding import EmbeddingRecord
```
