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

## Import Reference

```python
from tiferet_kb import Category
# or
from tiferet_kb.domain import Category
from tiferet_kb.domain.category import Category
```
