# tiferet-kb Service Interfaces

**Package:** `tiferet_kb.interfaces`

## Overview

Service interfaces define the abstract contracts that repositories implement.  All interfaces extend `tiferet.interfaces.Service` (an `ABC` subclass).  Domain events and contexts depend exclusively on these abstractions — never on concrete repository classes.

---

## CategoryService

**Module:** `tiferet_kb.interfaces.category`

Service interface for managing knowledge base categories.

### Methods

- **`exists(id: str) -> bool`** — Check if a category exists by ID.
- **`get(id: str)`** — Retrieve a category by ID.  Returns the aggregate, or `None`.
- **`list() -> List`** — List all categories.
- **`save(category) -> None`** — Save or update a category (upsert).
- **`delete(id: str) -> None`** — Delete a category by ID (idempotent).

---

## DocumentService

**Module:** `tiferet_kb.interfaces.document`

Service interface for managing documents, sections, and embeddings.

### Document Methods

- **`exists(id: str) -> bool`** — Check if a document exists by ID.
- **`get(id: str)`** — Retrieve a document by ID, including its sections.  Returns `None` if not found.
- **`list(folder_id=None, category_id=None, status=None, include_sections=False) -> List`** — List documents with optional filters.  When `include_sections=True`, each returned document includes its full section data.
- **`save(document) -> None`** — Save or update a document header (upsert).
- **`delete(id: str) -> None`** — Delete a document and all its sections (idempotent, cascading).

### Section Methods

- **`get_sections(document_id: str) -> List`** — Retrieve all sections for a document, ordered by position.
- **`save_section(section) -> None`** — Save or update a document section (upsert).
- **`delete_section(section_id: str) -> None`** — Delete a section by ID (idempotent).  Cascades to remove associated embeddings.
- **`reorder_sections(document_id: str, section_ids: List[str]) -> None`** — Reorder sections by providing the desired ordering of section IDs.

### Embedding Methods

- **`embed_section(section_id: str, embedding: List[float], model_name: str) -> None`** — Store or replace an embedding vector for a section.
- **`search_similar(query_embedding, limit=5, folder_id=None, category_id=None) -> List`** — Cosine similarity search over stored embeddings.  Returns dicts with `section_id` and `score`.
- **`get_embedding(section_id: str) -> Optional[List[float]]`** — Retrieve the stored embedding for a section, or `None`.
- **`remove_embedding(section_id: str) -> None`** — Remove a section's embedding without deleting the section.

---

## TemplateService

**Module:** `tiferet_kb.interfaces.template`

Service interface for managing knowledge base templates.

### Methods

- **`exists(id: str) -> bool`** — Check if a template exists by ID.
- **`get(id: str)`** — Retrieve a template by ID, including its sections.
- **`list(category_id=None) -> List`** — List templates, optionally filtered by category.
- **`save(template) -> None`** — Save or update a template header (upsert).
- **`save_section(section) -> None`** — Save or update a template section (upsert).
- **`delete(id: str) -> None`** — Delete a template and all its sections (idempotent, cascading).

---

## FolderService

**Module:** `tiferet_kb.interfaces.folder`

Service interface for managing knowledge base folders.

### Methods

- **`exists(id: str) -> bool`** — Check if a folder exists by ID.
- **`get(id: str)`** — Retrieve a folder by ID.
- **`list(parent_id=None) -> List`** — List folders.  `None` returns root-level folders.
- **`save(folder) -> None`** — Save or update a folder (upsert).
- **`delete(id: str) -> None`** — Delete a folder by ID (idempotent).
- **`move(id: str, new_parent_id=None) -> None`** — Move a folder to a new parent, or to root if `None`.

---

## Import Reference

```python
from tiferet_kb import CategoryService, DocumentService, TemplateService, FolderService
# or
from tiferet_kb.interfaces import CategoryService, DocumentService, TemplateService, FolderService
```
