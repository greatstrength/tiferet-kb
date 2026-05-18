# tiferet-kb Mappers

**Package:** `tiferet_kb.mappers`

## Overview

The mappers layer bridges tiferet-kb domain objects with HDF5 storage via tiferet-h5.  It provides two mapper types per domain concept:

| Class Type | Purpose | Base Class |
|---|---|---|
| **Aggregate** | Mutable domain operations | `tiferet.mappers.Aggregate` |
| **NodeObject** | HDF5 node attribute serialization | `tiferet_h5.mappers.NodeObject` |

Future phases will add **TableObject** mappers (from `tiferet_h5.mappers.TableObject`) for row-oriented entities like Documents, Templates, and Sections.

---

## CategoryAggregate

**Module:** `tiferet_kb.mappers.category`

Extends `Category` (domain object) with `Aggregate` (mutation base class).  Provides validated mutation methods for all mutable category fields.

### Mutation Methods

#### `rename(name: str) -> None`

Update the category name.  `validate_assignment=True` triggers Pydantic field validation.

```python
category = CategoryAggregate(id='notes', name='Notes')
category.rename('Meeting Notes')
```

#### `set_description(description: str | None) -> None`

Set or clear the category description.

#### `set_icon(icon: str | None) -> None`

Set or clear the category icon.

#### `set_color(color: str | None) -> None`

Set or clear the category hex color string.

### Generic Mutation

`set_attribute(attribute, value)` is inherited from `Aggregate` and validates the attribute name against `model_fields` before mutation.  Raises `INVALID_MODEL_ATTRIBUTE` for unknown attributes.

```python
category.set_attribute('name', 'Updated')     # OK
category.set_attribute('nonexistent', 'bad')   # raises TiferetError
```

---

## CategoryNodeObject

**Module:** `tiferet_kb.mappers.category`

Extends `Category` (domain object) with `NodeObject` (HDF5 attribute serialization).  Used by `CategoryH5Repository` to read/write category metadata as HDF5 group node attributes.

### Roles

```python
_ROLES = {
    'to_model': {},
    'to_h5.attrs': {'by_alias': True, 'exclude': {'id'}},
}
```

- **`to_model`** — Full serialization for mapping to aggregates.
- **`to_h5.attrs`** — Excludes `id` (encoded as the HDF5 group name) and applies aliases.

### Methods

#### `map(**overrides) -> CategoryAggregate`

Map the node object data to a `CategoryAggregate`.

```python
node_obj = CategoryNodeObject.from_attrs(attrs, id='meeting-notes')
aggregate = node_obj.map()
```

#### `from_model(category, **overrides) -> CategoryNodeObject` _(classmethod)_

Create a `CategoryNodeObject` from a `Category` model or aggregate.

```python
node_obj = CategoryNodeObject.from_model(aggregate)
attrs = node_obj.to_attrs()  # {'name': '...', 'description': '...', ...}
```

#### `to_attrs(role='to_h5.attrs', **overrides) -> Dict[str, Any]`

Inherited from `NodeObject`.  Serializes to a flat dict suitable for HDF5 `_v_attrs`.

#### `from_attrs(attrs, **overrides) -> CategoryNodeObject` _(classmethod)_

Inherited from `NodeObject`.  Constructs from an HDF5 attribute dict, decoding bytes and numpy scalars.

---

## HDF5 Storage Layout

```
/kb/
└── categories/
    ├── meeting-notes/       ← group node
    │   _v_attrs:
    │     name = 'Meeting Notes'
    │     description = 'Notes from meetings'
    │     icon = '📝'
    │     color = '#3B82F6'
    ├── design-docs/         ← group node
    │   _v_attrs:
    │     name = 'Design Docs'
    │     ...
```

The `id` is the group name.  All other fields are stored as node attributes via `CategoryNodeObject.to_attrs()`.

---

## Testing

Mapper tests use the harness pattern from `tiferet_kb.mappers.tests.settings`:

- **`AggregateTestBase`** — Inherits `test_new` and parametrized `test_set_attribute` for valid and invalid mutations.  Subclasses add domain-specific mutation tests.
- **`NodeObjectTestBase`** — Inherits `test_map`, `test_from_model`, `test_to_attrs_excludes_fields`, and `test_round_trip`.

The `conftest.py` hook dynamically parametrizes `test_set_attribute` from the class's `set_attribute_params` list.

---

## DocumentAggregate

**Module:** `tiferet_kb.mappers.document`

Extends `Document` with `Aggregate`.  Provides mutation methods for document fields.

### Mutation Methods

- **`rename(title: str) -> None`** — Update the document title.
- **`set_status(status: str) -> None`** — Update the document status (`draft`, `published`, `archived`).
- **`set_category(category_id: str | None) -> None`** — Set or clear the category.
- **`set_folder(folder_id: str | None) -> None`** — Set or clear the folder.
- **`touch() -> None`** — Update the `updated_at` timestamp to now.

---

## DocumentSectionAggregate

**Module:** `tiferet_kb.mappers.document`

Extends `DocumentSection` with `Aggregate`.  Provides mutation methods for section fields.

### Mutation Methods

- **`set_title(title: str) -> None`** — Update the section title.
- **`set_content(content: str) -> None`** — Update the section content.
- **`set_content_type(content_type: str) -> None`** — Update the content type.
- **`set_position(position: int) -> None`** — Update the ordering position.
- **`touch() -> None`** — Update `updated_at` timestamp.

---

## DocumentTableObject / DocumentSectionTableObject

**Module:** `tiferet_kb.mappers.document`

Extend `Document`/`DocumentSection` with `TableObject` (from `tiferet_h5.mappers`).  These provide row-level HDF5 serialization for table storage.

### Key Methods

- **`from_row(row) -> Self`** _(classmethod)_ — Construct from an HDF5 table row dict.
- **`from_model(model) -> Self`** _(classmethod)_ — Construct from a domain model or aggregate.
- **`to_row(table) -> None`** — Append a row to the HDF5 table.
- **`map(**overrides) -> Aggregate`** — Map to the corresponding aggregate.
- **`get_description() -> dict`** _(classmethod)_ — Return the PyTables column description.

---

## TemplateAggregate / TemplateSectionAggregate

**Module:** `tiferet_kb.mappers.template`

Extend `Template`/`TemplateSection` with `Aggregate`.

### TemplateAggregate Mutation Methods

- **`rename(name: str) -> None`**
- **`set_description(description: str | None) -> None`**
- **`set_category(category_id: str | None) -> None`**
- **`touch() -> None`**

### TemplateSectionAggregate Mutation Methods

- **`set_title(title: str) -> None`**
- **`set_default_content(default_content: str) -> None`**
- **`set_content_type(content_type: str) -> None`**
- **`set_position(position: int) -> None`**

---

## TemplateTableObject / TemplateSectionTableObject

**Module:** `tiferet_kb.mappers.template`

Extend `Template`/`TemplateSection` with `TableObject`.  Same row-level HDF5 serialization pattern as the document mappers.

---

## FolderAggregate

**Module:** `tiferet_kb.mappers.folder`

Extends `Folder` with `Aggregate`.

### Mutation Methods

- **`rename(name: str) -> None`**
- **`set_parent(parent_id: str | None, path: str) -> None`** — Update the parent and materialized path.

---

## FolderNodeObject

**Module:** `tiferet_kb.mappers.folder`

Extends `Folder` with `NodeObject`.  Same HDF5 node-attribute serialization pattern as `CategoryNodeObject`.

### Roles

```python
_ROLES = {
    'to_model': {},
    'to_h5.attrs': {'by_alias': True, 'exclude': {'id'}},
}
```

---

## EmbeddingRecordAggregate

**Module:** `tiferet_kb.mappers.embedding`

Extends `EmbeddingRecord` with `Aggregate`.  Minimal aggregate — embedding records are primarily created and deleted, not mutated.

---

## HDF5 Storage Layout

```
/kb/
├── categories/<id>/           ← CategoryNodeObject attrs
├── documents/
│   ├── documents              ← DocumentTableObject rows
│   ├── document_sections      ← DocumentSectionTableObject rows
│   ├── section_embeddings     ← float32 numpy array
│   └── section_embedding_ids   ← string index array
├── templates/
│   ├── templates              ← TemplateTableObject rows
│   └── template_sections      ← TemplateSectionTableObject rows
└── folders/<id>/              ← FolderNodeObject attrs
```

---

## Import Reference

```python
from tiferet_kb import (
    CategoryAggregate, CategoryNodeObject,
    DocumentAggregate, DocumentSectionAggregate,
    DocumentTableObject, DocumentSectionTableObject,
    TemplateAggregate, TemplateSectionAggregate,
    TemplateTableObject, TemplateSectionTableObject,
    FolderAggregate, FolderNodeObject,
    EmbeddingRecordAggregate,
)
```
