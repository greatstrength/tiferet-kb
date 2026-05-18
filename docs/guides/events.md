# tiferet-kb Domain Events

**Package:** `tiferet_kb.events`

## Overview

Domain events are the primary operational units in tiferet-kb.  Each event encapsulates a single, well-defined domain operation — creating a category, retrieving a document, moving a folder.  They follow the standard Tiferet DDD event pattern:

- Extend `tiferet.events.DomainEvent`.
- Receive dependencies via constructor injection (usually a Service).
- Expose an `execute(**kwargs)` method as the entry point.
- Use `@DomainEvent.parameters_required([...])` for declarative input validation.
- Use `verify()` for domain-specific rule enforcement.
- Are invoked in tests via `DomainEvent.handle()`.

---

## Category Events

**Module:** `tiferet_kb.events.category`

All category events depend on `CategoryService` injected via the constructor.

### AddCategory

Creates a new knowledge base category.

**Required parameters:** `id`, `name`
**Optional parameters:** `description`, `icon`, `color`

**Behavior:**
1. Constructs a `CategoryAggregate` from the input parameters.
2. Verifies no category with the same `id` already exists (`KB_CATEGORY_ALREADY_EXISTS`).
3. Persists via `category_service.save()`.
4. Returns the created `Category`.

```python
from tiferet.events import DomainEvent
from tiferet_kb.events import AddCategory

result = DomainEvent.handle(
    AddCategory,
    dependencies={'category_service': category_service},
    id='meeting-notes',
    name='Meeting Notes',
    description='Notes from team meetings',
    icon='📝',
    color='#3B82F6',
)
```

### GetCategory

Retrieves a category by its identifier.

**Required parameters:** `id`

**Behavior:**
1. Retrieves the category from the service.
2. Verifies the category exists (`KB_CATEGORY_NOT_FOUND`).
3. Returns the `Category`.

```python
result = DomainEvent.handle(
    GetCategory,
    dependencies={'category_service': category_service},
    id='meeting-notes',
)
```

### ListCategories

Lists all knowledge base categories.

**Required parameters:** _(none)_

**Behavior:** Delegates to `category_service.list()` and returns the full list.

```python
result = DomainEvent.handle(
    ListCategories,
    dependencies={'category_service': category_service},
)
```

### UpdateCategory

Updates an existing category's metadata.

**Required parameters:** `id`, `attribute`
**Optional parameters:** `value`

**Supported attributes:** `name`, `description`, `icon`, `color`

**Behavior:**
1. Validates the attribute name is supported (`KB_INVALID_CATEGORY_ATTRIBUTE`).
2. For `name`, validates a non-empty string is provided.
3. Retrieves the category (`KB_CATEGORY_NOT_FOUND` if absent).
4. Applies the mutation via the aggregate's typed setter method.
5. Persists and returns the updated `Category`.

```python
result = DomainEvent.handle(
    UpdateCategory,
    dependencies={'category_service': category_service},
    id='meeting-notes',
    attribute='name',
    value='Team Meeting Notes',
)
```

### RemoveCategory

Removes a category by ID.  This operation is idempotent — deleting a non-existent category succeeds silently.

**Required parameters:** `id`

**Behavior:** Delegates to `category_service.delete()` and returns the removed `id`.

```python
result = DomainEvent.handle(
    RemoveCategory,
    dependencies={'category_service': category_service},
    id='meeting-notes',
)
# result == 'meeting-notes'
```

---

## Error Codes

| Constant | When Raised |
|---|---|
| `KB_CATEGORY_NOT_FOUND` | `GetCategory` or `UpdateCategory` when the category does not exist. |
| `KB_CATEGORY_ALREADY_EXISTS` | `AddCategory` when a category with the same ID already exists. |
| `KB_INVALID_CATEGORY_ATTRIBUTE` | `UpdateCategory` when the attribute name is not supported. |

---

## Testing Events

Always use `DomainEvent.handle()` in tests with a mocked service:

```python
from unittest import mock
from tiferet.events import DomainEvent
from tiferet_kb.events import GetCategory
from tiferet_kb.interfaces import CategoryService

mock_service = mock.Mock(spec=CategoryService)
mock_service.get.return_value = sample_category

result = DomainEvent.handle(
    GetCategory,
    dependencies={'category_service': mock_service},
    id='meeting-notes',
)

assert result is sample_category
mock_service.get.assert_called_once_with('meeting-notes')
```

---

---

## Section Events

**Module:** `tiferet_kb.events.document`

All section events depend on `DocumentService` injected via the constructor.

### AddDocumentSection

Adds a new section to an existing document.

**Required parameters:** `document_id`, `title`, `content_type`
**Optional parameters:** `content`, `position`

**Behavior:**
1. Validates `content_type` is one of `text`, `markdown`, `code`, `table`, `image` (`KB_INVALID_CONTENT_TYPE`).
2. Verifies the parent document exists (`KB_DOCUMENT_NOT_FOUND`).
3. If `position` is not provided, appends to the end.
4. Creates and persists a `DocumentSectionAggregate`.
5. Returns the created `DocumentSection`.

```python
result = DomainEvent.handle(
    AddDocumentSection,
    dependencies={'document_service': doc_service},
    document_id='doc-001',
    title='Introduction',
    content_type='markdown',
    content='# Welcome',
)
```

### UpdateDocumentSection

Updates a section's content or metadata.

**Required parameters:** `id`, `attribute`, `document_id` (via kwargs)
**Supported attributes:** `title`, `content`, `content_type`

**Behavior:**
1. Validates the attribute name (`KB_INVALID_SECTION_ATTRIBUTE`).
2. For `content_type`, validates the value (`KB_INVALID_CONTENT_TYPE`).
3. Retrieves the section by `id` within the document's section list.
4. Applies the mutation and persists.

```python
result = DomainEvent.handle(
    UpdateDocumentSection,
    dependencies={'document_service': doc_service},
    id='sec-001',
    attribute='content',
    value='Updated content here',
    document_id='doc-001',
)
```

### RemoveDocumentSection

Removes a section by ID. Idempotent.

**Required parameters:** `id`

```python
result = DomainEvent.handle(
    RemoveDocumentSection,
    dependencies={'document_service': doc_service},
    id='sec-001',
)
```

### ReorderDocumentSections

Reorders sections within a document by providing the desired ordering of section IDs.

**Required parameters:** `document_id`, `section_ids`

```python
result = DomainEvent.handle(
    ReorderDocumentSections,
    dependencies={'document_service': doc_service},
    document_id='doc-001',
    section_ids=['sec-003', 'sec-001', 'sec-002'],
)
```

---

## Section Error Codes

| Constant | When Raised |
|---|---|
| `KB_DOCUMENT_NOT_FOUND` | `AddDocumentSection` / `ReorderDocumentSections` when the parent document does not exist. |
| `KB_DOCUMENT_SECTION_NOT_FOUND` | `UpdateDocumentSection` when the section ID is not found. |
| `KB_INVALID_SECTION_ATTRIBUTE` | `UpdateDocumentSection` when the attribute name is not supported. |
| `KB_INVALID_CONTENT_TYPE` | `AddDocumentSection` / `UpdateDocumentSection` when the content type is invalid. |

---

## Template Events

**Module:** `tiferet_kb.events.template`

All template events depend on `TemplateService` injected via the constructor.

### AddTemplate

Creates a new knowledge base template.

**Required parameters:** `name`
**Optional parameters:** `description`, `category_id`

**Behavior:**
1. Constructs a `TemplateAggregate` from the input parameters.
2. Verifies no template with the same `id` already exists (`KB_TEMPLATE_ALREADY_EXISTS`).
3. Persists via `template_service.save()`.
4. Returns the created `Template`.

### GetTemplate

Retrieves a template by its identifier, including its sections.

**Required parameters:** `id`

**Behavior:**
1. Retrieves the template from the service.
2. Verifies the template exists (`KB_TEMPLATE_NOT_FOUND`).
3. Returns the `Template`.

### ListTemplates

Lists all templates, optionally filtered by category.

**Optional parameters:** `category_id`

### UpdateTemplate

Updates an existing template's metadata.

**Required parameters:** `id`, `attribute`
**Optional parameters:** `value`

**Supported attributes:** `name`, `description`, `category_id`

### RemoveTemplate

Removes a template by ID.  Idempotent.

**Required parameters:** `id`

### ApplyTemplate

Stamps a template's section blueprints into new document sections, creating a new document with the template's suggested category.

**Required parameters:** `template_id`, `title`
**Optional parameters:** `folder_id`, `category_id` (overrides template's default)

**Behavior:**
1. Retrieves the template (`KB_TEMPLATE_NOT_FOUND` if absent).
2. Creates a new `DocumentAggregate` with the template's category (unless overridden).
3. Stamps each `TemplateSection` into a new `DocumentSectionAggregate`.
4. Persists the document and all sections.
5. Returns the created `Document`.

---

## Template Error Codes

| Constant | When Raised |
|---|---|
| `KB_TEMPLATE_NOT_FOUND` | `GetTemplate`, `UpdateTemplate`, `ApplyTemplate` when the template does not exist. |
| `KB_TEMPLATE_ALREADY_EXISTS` | `AddTemplate` when a template with the same ID already exists. |

---

## Folder Events

**Module:** `tiferet_kb.events.folder`

All folder events depend on `FolderService` injected via the constructor.  Some also depend on `DocumentService`.

### AddFolder

Creates a new folder in the hierarchy.

**Required parameters:** `name`
**Optional parameters:** `parent_id`

**Behavior:**
1. Constructs a `FolderAggregate`.
2. If `parent_id` is provided, verifies the parent folder exists (`KB_FOLDER_NOT_FOUND`).
3. Persists and returns the created `Folder`.

### GetFolder

Retrieves a folder by its identifier.

**Required parameters:** `id`

### ListFolderContents

Lists folders under a given parent.

**Optional parameters:** `parent_id`

### MoveFolder

Moves a folder to a new parent, updating its materialized path.

**Required parameters:** `id`
**Optional parameters:** `new_parent_id`

**Behavior:** Verifies the folder and (optionally) the target parent exist.  Checks for circular references (`KB_FOLDER_CIRCULAR_REFERENCE`).

### MoveDocument

Moves a document to a different folder.

**Required parameters:** `document_id`
**Optional parameters:** `folder_id`

### RemoveFolder

Removes a folder by ID.  Idempotent.

**Required parameters:** `id`

---

## Folder Error Codes

| Constant | When Raised |
|---|---|
| `KB_FOLDER_NOT_FOUND` | `GetFolder`, `MoveFolder`, `AddFolder` (parent check). |
| `KB_FOLDER_ALREADY_EXISTS` | `AddFolder` when duplicate. |
| `KB_FOLDER_CIRCULAR_REFERENCE` | `MoveFolder` when the target parent creates a cycle. |

---

## Embedding Events

**Module:** `tiferet_kb.events.embedding`

All embedding events depend on `DocumentService` injected via the constructor.

### EmbedDocumentSections

Stores or replaces embedding vectors for one or more document sections.

**Required parameters:** `section_ids`, `embeddings`, `model_name`

**Behavior:** Iterates over the section IDs and corresponding embedding vectors, calling `document_service.embed_section()` for each.  Validates dimension consistency across calls.

### SearchSimilarSections

Performs cosine similarity search over stored embeddings.

**Required parameters:** `query_embedding`
**Optional parameters:** `limit`, `folder_id`, `category_id`

**Returns:** A list of dicts with `section_id` and `score`, ranked by descending similarity.

### RemoveEmbedding

Removes the embedding for a section without deleting the section itself.

**Required parameters:** `section_id`

---

## Embedding Error Codes

| Constant | When Raised |
|---|---|
| `KB_EMBEDDING_DIMENSION_MISMATCH` | `EmbedDocumentSections` when vector dimensions are inconsistent. |
| `KB_EMBEDDING_NOT_FOUND` | When the embedding does not exist. |

---

## Import Reference

```python
from tiferet_kb.events import (
    # Category
    AddCategory, GetCategory, ListCategories, UpdateCategory, RemoveCategory,
    # Document
    AddDocument, GetDocument, ListDocuments, UpdateDocument, RemoveDocument,
    AddDocumentSection, UpdateDocumentSection, RemoveDocumentSection, ReorderDocumentSections,
    # Template
    AddTemplate, GetTemplate, ListTemplates, UpdateTemplate, RemoveTemplate, ApplyTemplate,
    # Embedding
    EmbedDocumentSections, SearchSimilarSections, RemoveEmbedding,
    # Folder
    AddFolder, GetFolder, ListFolderContents, MoveFolder, MoveDocument, RemoveFolder,
)
```
