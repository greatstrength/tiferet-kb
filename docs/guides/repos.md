# tiferet-kb Repositories

**Package:** `tiferet_kb.repos`

## Overview

Repositories are the concrete data-access layer in tiferet-kb.  Every repository implements a Service interface from `tiferet_kb.interfaces` and uses `tiferet_h5.H5Repository` as its base for HDF5 file access.

Repositories are **never exported** from `tiferet_kb.repos.__init__.py` — they are resolved at runtime through DI configuration.  Consuming code depends only on the abstract Service interface.

---

## CategoryH5Repository

**Module:** `tiferet_kb.repos.category`

Implements `CategoryService` using HDF5 group node attributes for storage.  Each category is stored as a group node at `/kb/categories/<id>` with scalar metadata written as `_v_attrs` entries via `CategoryNodeObject`.

### Constructor

```python
CategoryH5Repository(h5_file: str, mode: str = 'a')
```

- **`h5_file`** — Path to the HDF5 file.
- **`mode`** — Default PyTables open mode (`'a'` = append/create-if-absent).

### Method Patterns

Each method opens a short-lived `H5Client` via `self.client()` as a context manager:

#### `exists(id: str) -> bool`

Checks whether the group node `/kb/categories/<id>` exists.

```python
with self.client(mode='r') as h5:
    return h5.node_exists(f'/kb/categories/{id}')
```

#### `get(id: str) -> CategoryAggregate | None`

Reads group attributes and maps them to a `CategoryAggregate`.  Returns `None` if the group does not exist.

```python
with self.client(mode='r') as h5:
    if not h5.node_exists(group_path):
        return None
    attrs = h5.get_node_attrs(group_path)

return CategoryNodeObject.from_attrs(attrs, id=id).map()
```

The `id` is injected as an override because it's encoded as the group name, not as a node attribute.

#### `list() -> List[CategoryAggregate]`

Iterates child groups under `/kb/categories/` and maps each to an aggregate.

#### `save(category: CategoryAggregate) -> None`

Upserts a category:
1. Converts the aggregate to a `CategoryNodeObject` via `from_model()`.
2. Serializes to an attribute dict via `to_attrs()`.
3. Creates the group if absent; writes each attribute via `set_node_attr()`.

```python
node_obj = CategoryNodeObject.from_model(category)
attr_data = node_obj.to_attrs()

with self.client() as h5:
    if not h5.node_exists(group_path):
        h5.create_group(group_path, title=category.name)
    for attr_name, attr_value in attr_data.items():
        h5.set_node_attr(group_path, attr_name, attr_value)
```

#### `delete(id: str) -> None`

Removes the group node and all its contents.  Idempotent — silently succeeds if the group does not exist.

```python
with self.client() as h5:
    if not h5.node_exists(group_path):
        return
    h5.h5file.remove_node(group_path, recursive=True)
```

---

## HDF5 File Structure

After creating several categories:

```
/kb/
└── categories/              ← root group (title: 'Knowledge Base Categories')
    ├── meeting-notes/       ← category group
    │   _v_attrs: name, description, icon, color
    ├── design-docs/         ← category group
    │   _v_attrs: name, description, icon, color
    └── api-specs/           ← category group
        _v_attrs: name, description, icon, color
```

---

## Testing

Repository tests are **integration tests** that operate against real temporary HDF5 files, not mocks.  This validates the full round-trip through `H5Client`, `CategoryNodeObject`, and PyTables.

**Fixtures:**
- `h5_file(tmp_path)` — provides a temporary `.h5` file path.
- `category_repo(h5_file)` — provides a `CategoryH5Repository` instance.
- `sample_category()` — provides a `CategoryAggregate` for testing.

**Standard test cases:**
- `test_int_save_and_exists` — save then verify exists.
- `test_int_exists_negative` — non-existent returns False.
- `test_int_get_success` — round-trip save/get with field verification.
- `test_int_get_not_found` — missing returns None.
- `test_int_list_categories` — enumerate multiple categories.
- `test_int_list_empty` — empty list when root group has no children.
- `test_int_save_update` — mutate and re-save preserves updates.
- `test_int_delete_success` — delete removes the category.
- `test_int_delete_idempotent` — deleting non-existent succeeds.

---

## DI Registration

Register the repository in the container configuration:

```yaml
services:
  category_service:
    module_path: tiferet_kb.repos.category
    class_name: CategoryH5Repository
    params:
      h5_file: data/kb.h5
```

---

## DocumentH5Repository

**Module:** `tiferet_kb.repos.document`

Implements `DocumentService` using HDF5 tables for document and section storage, with parallel numpy arrays for embeddings.

### Constructor

```python
DocumentH5Repository(h5_file: str, mode: str = 'a')
```

### HDF5 Layout

```
/kb/documents/
├── documents              ← DocumentTableObject rows
├── document_sections      ← DocumentSectionTableObject rows
├── section_embeddings     ← float32 numpy array
└── section_embedding_ids   ← S64 string index array
```

### Key Behaviors

- **`get(id)`** — Joins header and section rows to return a fully-populated aggregate.
- **`list(include_sections=True)`** — Optionally loads sections for each document (avoids N+1 workaround).
- **`delete(id)`** — Cascading: removes the document row, all section rows, and all associated embedding entries.
- **`embed_section()`** — Uses parallel HDF5 arrays for embedding storage.  Replaces existing vectors; validates dimension consistency.
- **`search_similar()`** — Brute-force cosine similarity over all stored embeddings with optional folder/category filtering.

---

## TemplateH5Repository

**Module:** `tiferet_kb.repos.template`

Implements `TemplateService` using HDF5 tables for template and template section storage.

### Constructor

```python
TemplateH5Repository(h5_file: str, mode: str = 'a')
```

### HDF5 Layout

```
/kb/templates/
├── templates              ← TemplateTableObject rows
└── template_sections      ← TemplateSectionTableObject rows
```

### Key Behaviors

- **`get(id)`** — Joins header and section rows.
- **`delete(id)`** — Cascading: removes template and all section rows.
- **`save_section()`** — Upserts a template section.

---

## FolderH5Repository

**Module:** `tiferet_kb.repos.folder`

Implements `FolderService` using HDF5 group node attributes, similar to `CategoryH5Repository`.

### Constructor

```python
FolderH5Repository(h5_file: str, mode: str = 'a')
```

### HDF5 Layout

```
/kb/folders/
├── <uuid-1>/              ← FolderNodeObject attrs
├── <uuid-2>/              ← FolderNodeObject attrs
└── ...
```

### Key Behaviors

- **`list(parent_id=None)`** — Filters by `parent_id` attribute.  `None` returns root-level folders.
- **`move(id, new_parent_id)`** — Updates `parent_id` and `path` attributes on the group node.
- **`delete(id)`** — Removes the group node and all its attributes (idempotent).

---

## Testing

All repository tests are **integration tests** against real temporary HDF5 files:

- `tiferet_kb/repos/tests/test_category.py`
- `tiferet_kb/repos/tests/test_document.py`
- `tiferet_kb/repos/tests/test_template.py`
- `tiferet_kb/repos/tests/test_folder.py`

Cross-domain integration tests live in `tiferet_kb/tests_int/test_workflow.py`.

---

## Import Reference

Repositories are not exported from `__init__.py`.  For testing or direct use:

```python
from tiferet_kb.repos.category import CategoryH5Repository
from tiferet_kb.repos.document import DocumentH5Repository
from tiferet_kb.repos.template import TemplateH5Repository
from tiferet_kb.repos.folder import FolderH5Repository
```
