# tiferet-kb

A Knowledge Base extension for the [Tiferet](https://github.com/greatstrength/tiferet) framework with HDF5-backed storage via [tiferet-h5](https://github.com/greatstrength/tiferet-h5).

## Overview

**tiferet-kb** provides a Domain-Driven Design (DDD) layer for building knowledge base applications — managing documents, sections, categories, templates, and folder hierarchies. Built on the Tiferet framework and backed by HDF5 for efficient structured storage.

## Installation

```bash
pip install tiferet-kb
```

**Requirements:** Python ≥ 3.10, tiferet ≥ 2.0.0b3, tiferet-h5 ≥ 0.1.0

## Current Status (v0.1.0a1)

Phase 1 — Category domain:
- **Domain:** `Category` domain object
- **Interface:** `CategoryService` abstract service contract
- **Mappers:** `CategoryAggregate` (mutable) + `CategoryNodeObject` (HDF5 node attributes)
- **Repository:** `CategoryH5Repository` — HDF5-backed persistence using group node attributes
- **Events:** `AddCategory`, `GetCategory`, `ListCategories`, `UpdateCategory`, `RemoveCategory`

## Architecture

```
tiferet_kb/
├── assets/         Error code constants
├── domain/         DomainObject subclasses
├── interfaces/     Service ABC contracts
├── mappers/        Aggregate + NodeObject/TableObject mappers
├── events/         DomainEvent subclasses
└── repos/          H5Repository implementations
```

## License

BSD 3-Clause License. See [LICENSE](LICENSE) for details.
