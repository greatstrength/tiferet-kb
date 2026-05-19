# tiferet_kb Examples

## kb_demo.py

Demonstrates the core knowledge base workflow:

1. **Create a category** — `AddCategory` event
2. **Import a markdown document** — `ImportMarkdownDocument` event parses H1-delimited sections
3. **List documents** — `ListDocuments` event
4. **Export to markdown** — `ExportDocumentMarkdown` event reconstructs the markdown

### Run

```bash
python examples/kb_demo.py
```

The demo uses mock services so no HDF5 file is required.

## Markdown Convention

tiferet_kb uses a simple, agent-friendly convention for markdown documents:

- **Every document must start with an `# H1` heading.**
- Each `# H1` heading begins a new section.
- Sub-headings (`##`, `###`, etc.) and all other content belong to the current section.
- The first H1's text becomes the document title.

### Example

```markdown
# Introduction

Welcome to the knowledge base.

## Prerequisites

- Python 3.10+

# Getting Started

Follow these steps to begin.
```

This produces two sections:

| Position | Title            | Content includes             |
|----------|------------------|------------------------------|
| 0        | Introduction     | Paragraphs + ## Prerequisites |
| 1        | Getting Started  | "Follow these steps..."       |

This convention is intentionally simple — it is trivial to teach to AI agents
generating knowledge base content programmatically.
