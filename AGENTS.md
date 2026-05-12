# AGENTS.md — tiferet-kb

## Project Overview

**tiferet-kb** is a Knowledge Base extension package for the [Tiferet](https://github.com/greatstrength/tiferet) framework.  It provides a full Domain-Driven Design (DDD) layer for managing documents, sections, categories, templates, and folder hierarchies, backed by HDF5 storage via [tiferet-h5](https://github.com/greatstrength/tiferet-h5).

- **Repository:** https://github.com/greatstrength/tiferet-kb
- **Branch:** `v0.x-proto`
- **Python:** ≥ 3.10
- **Version:** `0.1.0a1`
- **Dependencies:** `tiferet >= 2.0.0b3`, `tiferet-h5 >= 0.1.0`

## Architecture

### Layer Overview

```
tiferet_kb/
├── assets/         Error code string constants
├── domain/         DomainObject subclasses (Category, Document, DocumentSection, Template, TemplateSection, Folder)
├── interfaces/     Service ABC contracts (CategoryService, DocumentService, TemplateService, FolderService)
├── mappers/        Aggregate + NodeObject + TableObject mappers
├── events/         DomainEvent subclasses (~26 events across 4 domains)
├── repos/          H5Repository implementations
└── tests_int/      Cross-domain integration tests
```

### Key Concepts

**Storage Patterns:**
- **NodeObject** (group attributes) — Used for lightweight, scalar-metadata entities: `Category` at `/kb/categories/<id>`, `Folder` at `/kb/folders/<id>`.
- **TableObject** (table rows) — Used for high-volume, query-filtered collections: `Document`/`DocumentSection` at `/kb/documents/`, `Template`/`TemplateSection` at `/kb/templates/`.

**HDF5 Layout:**
```
/kb/
├── categories/<id>/          ← NodeObject attrs: name, description, icon, color
├── documents/
│   ├── documents             ← TableObject rows: id, title, category_id, status, ...
│   └── document_sections     ← TableObject rows: id, document_id, title, content, position, ...
├── templates/
│   ├── templates             ← TableObject rows: id, name, description, category_id, ...
│   └── template_sections     ← TableObject rows: id, template_id, title, default_content, position, ...
└── folders/<id>/             ← NodeObject attrs: name, parent_id, path, created_at
```

### Domain Objects

All extend `tiferet.domain.DomainObject` (Pydantic v2, read-only).

- **Category** — Slug-style id, name, description, icon, color.
- **Document** — UUID id (auto-generated), title, category_id, template_id, folder_id, status, timestamps, sections list.
- **DocumentSection** — UUID id, document_id, title, content_type, content, position, timestamps.
- **Template** — UUID id, name, description, category_id, timestamps, sections list.
- **TemplateSection** — UUID id, template_id, title, content_type, default_content, position.
- **Folder** — UUID id, name, parent_id, materialized path, created_at.

### Events

26 domain events across 4 groups:

- **Category:** AddCategory, GetCategory, ListCategories, UpdateCategory, RemoveCategory
- **Document:** AddDocument, GetDocument, ListDocuments, UpdateDocument, RemoveDocument, AddDocumentSection, UpdateDocumentSection, RemoveDocumentSection, ReorderDocumentSections
- **Template:** AddTemplate, GetTemplate, ListTemplates, UpdateTemplate, RemoveTemplate, ApplyTemplate
- **Folder:** AddFolder, GetFolder, ListFolderContents, MoveFolder, MoveDocument, RemoveFolder

Key cross-domain event: **ApplyTemplate** stamps template sections into new document sections, inheriting the template's suggested category.

## Structured Code Style

All code follows the Tiferet artifact comment hierarchy.  **This is mandatory.**

### Comment Levels

- `# *** <section>` — Top-level: `imports`, `constants`, `models`, `mappers`, `events`, `repos`, `interfaces`
- `# ** <category>: <name>` — Mid-level: `core`, `infra`, `app` (imports); `model:`, `mapper:`, `event:`, `repo:`, `interface:`
- `# * <component>` — Low-level: `attribute: <name>`, `init`, `method: <name>`, `method: <name> (static)`

### Spacing Rules

- One empty line between `# ***` and first `# **`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

### Docstrings

RST format with `:param`, `:type`, `:return:`, `:rtype:` for all public methods.

## Testing

- **Framework:** `pytest` (with `pytest-cov`).
- **Test location:** Co-located in `<package>/tests/` directories.
- **Integration tests:** `tiferet_kb/tests_int/`.
- **Mapper test harness:** `mappers/tests/settings.py` provides `AggregateTestBase` and `NodeObjectTestBase`.
- **Event testing:** Always invoke via `DomainEvent.handle(EventClass, dependencies={...}, **kwargs)`.
- **Repo testing:** Integration tests with `tmp_path`-based real HDF5 files.
- **Run tests:** `pytest --verbose` from project root.

## Error Handling

All errors are raised as `TiferetError` via `self.verify()` or `self.raise_error()` in domain events.  Error code constants are defined in `tiferet_kb/assets/constants.py`.  Error definitions with multilingual messages are in `app/configs/error.yml`.

## Package Exports

`tiferet_kb/__init__.py` exports:

- **Domain:** Category, Document, DocumentSection, Template, TemplateSection, Folder
- **Interfaces:** CategoryService, DocumentService, TemplateService, FolderService
- **Mappers:** All Aggregate, NodeObject, and TableObject classes

## Key Files for Orientation

- `tiferet_kb/__init__.py` — Version and public exports
- `tiferet_kb/assets/constants.py` — KB error code constants
- `tiferet_kb/domain/` — All domain objects
- `tiferet_kb/interfaces/` — All service contracts
- `tiferet_kb/mappers/` — All mapper classes
- `tiferet_kb/events/` — All domain events
- `tiferet_kb/repos/` — All H5 repository implementations
- `tiferet_kb/tests_int/test_workflow.py` — End-to-end integration test
- `app/configs/` — YAML configuration files (app, container, feature, error)

## Contributing

1. Work from the `v0.x-proto` branch.  Feature branches: `<issue-number>-<lowercase-hyphenated-title>`.
2. Follow the structured code style documented above.
3. All errors must use `self.verify()` or `self.raise_error()` with a constant from `assets/constants.py`.
4. Separate functional changes from documentation in distinct commits.
5. Include `Co-Authored-By: Oz <oz-agent@warp.dev>` in every commit made with AI assistance.
