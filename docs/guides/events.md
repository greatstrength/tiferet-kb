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

## Import Reference

```python
from tiferet_kb.events import (
    AddCategory,
    GetCategory,
    ListCategories,
    UpdateCategory,
    RemoveCategory,
)
```
