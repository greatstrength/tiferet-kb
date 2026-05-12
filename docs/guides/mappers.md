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

## Import Reference

```python
from tiferet_kb import CategoryAggregate, CategoryNodeObject
# or
from tiferet_kb.mappers import CategoryAggregate, CategoryNodeObject
```
