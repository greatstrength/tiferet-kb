"""tiferet_kb End-to-End Workflow Integration Tests

Validates the full cross-domain workflow using real HDF5 repositories:
  1. Create categories
  2. Create a template with sections
  3. Apply the template to create a document
  4. Create folders and move the document into a folder
  5. Update, reorder, and delete operations across domains
"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.events import DomainEvent

from ..repos.category import CategoryH5Repository
from ..repos.document import DocumentH5Repository
from ..repos.template import TemplateH5Repository
from ..repos.folder import FolderH5Repository
from ..mappers import CategoryAggregate
from ..events import (
    AddCategory,
    AddDocument,
    AddTemplate,
    ApplyTemplate,
    GetDocument,
    AddDocumentSection,
    UpdateDocument,
    ReorderDocumentSections,
    AddFolder,
    MoveDocument,
    ListFolderContents,
    RemoveDocument,
    RemoveFolder,
    EmbedDocumentSections,
    SearchSimilarSections,
    RemoveEmbedding,
)

# *** fixtures

# ** fixture: h5_file
@pytest.fixture
def h5_file(tmp_path) -> str:
    '''Provide a single temporary HDF5 file for all repos.'''
    return str(tmp_path / 'kb.h5')


# ** fixture: category_repo
@pytest.fixture
def category_repo(h5_file) -> CategoryH5Repository:
    '''Category repository.'''
    return CategoryH5Repository(h5_file=h5_file)


# ** fixture: doc_repo
@pytest.fixture
def doc_repo(h5_file) -> DocumentH5Repository:
    '''Document repository.'''
    return DocumentH5Repository(h5_file=h5_file)


# ** fixture: template_repo
@pytest.fixture
def template_repo(h5_file) -> TemplateH5Repository:
    '''Template repository.'''
    return TemplateH5Repository(h5_file=h5_file)


# ** fixture: folder_repo
@pytest.fixture
def folder_repo(h5_file) -> FolderH5Repository:
    '''Folder repository.'''
    return FolderH5Repository(h5_file=h5_file)

# *** tests

# ** test_int: full_workflow
def test_int_full_workflow(category_repo, doc_repo, template_repo, folder_repo):
    '''
    End-to-end test: category → template → apply → folder → move → cleanup.
    '''

    # --- Step 1: Create a category ---
    category = DomainEvent.handle(
        AddCategory,
        dependencies={'category_service': category_repo},
        id='meeting-notes',
        name='Meeting Notes',
        icon='📝',
    )
    assert category.id == 'meeting-notes'

    # --- Step 2: Create a template with sections ---
    template = DomainEvent.handle(
        AddTemplate,
        dependencies={'template_service': template_repo},
        name='Sprint Retro',
        category_id='meeting-notes',
        sections=[
            {'title': 'What went well', 'content_type': 'markdown', 'default_content': '- '},
            {'title': 'What to improve', 'content_type': 'markdown', 'default_content': '- '},
            {'title': 'Action items', 'content_type': 'text', 'default_content': ''},
        ],
    )
    assert template.name == 'Sprint Retro'

    # Verify template sections were persisted.
    full_template = template_repo.get(template.id)
    assert len(full_template.sections) == 3

    # --- Step 3: Apply the template to create a document ---
    document = DomainEvent.handle(
        ApplyTemplate,
        dependencies={
            'template_service': template_repo,
            'document_service': doc_repo,
        },
        template_id=template.id,
        title='Sprint 42 Retro',
    )
    assert document.title == 'Sprint 42 Retro'
    assert document.template_id == template.id
    assert document.category_id == 'meeting-notes'

    # Verify the document has stamped sections.
    full_doc = DomainEvent.handle(
        GetDocument,
        dependencies={'document_service': doc_repo},
        id=document.id,
    )
    assert full_doc.section_count() == 3
    assert full_doc.sections[0].title == 'What went well'

    # --- Step 4: Add an extra section ---
    extra_section = DomainEvent.handle(
        AddDocumentSection,
        dependencies={'document_service': doc_repo},
        document_id=document.id,
        title='Notes',
        content='Additional **notes** here.',
    )
    assert extra_section.position == 3
    # Verify rich-text parsing occurred.
    assert len(extra_section.paragraphs) == 1
    assert extra_section.paragraphs[0].segments[1].format_type == 'bold'

    # --- Step 5: Reorder sections (move 'Notes' to position 0) ---
    sections = doc_repo.get_sections(document.id)
    section_ids = [s.id for s in sections]
    new_order = [section_ids[3], section_ids[0], section_ids[1], section_ids[2]]

    DomainEvent.handle(
        ReorderDocumentSections,
        dependencies={'document_service': doc_repo},
        document_id=document.id,
        section_ids=new_order,
    )

    reordered = doc_repo.get_sections(document.id)
    assert reordered[0].title == 'Notes'
    assert reordered[1].title == 'What went well'

    # --- Step 6: Create a folder and move the document into it ---
    folder = DomainEvent.handle(
        AddFolder,
        dependencies={'folder_service': folder_repo},
        name='Sprint Retros',
    )
    assert folder.path == '/Sprint Retros'

    DomainEvent.handle(
        MoveDocument,
        dependencies={'document_service': doc_repo},
        document_id=document.id,
        folder_id=folder.id,
    )

    # Verify the document is in the folder.
    moved_doc = doc_repo.get(document.id)
    assert moved_doc.folder_id == folder.id

    # --- Step 7: List folder contents ---
    contents = DomainEvent.handle(
        ListFolderContents,
        dependencies={
            'folder_service': folder_repo,
            'document_service': doc_repo,
        },
        folder_id=folder.id,
    )
    assert len(contents['documents']) == 1
    assert contents['documents'][0].id == document.id

    # --- Step 8: Update the document status ---
    DomainEvent.handle(
        UpdateDocument,
        dependencies={'document_service': doc_repo},
        id=document.id,
        attribute='status',
        value='published',
    )
    published_doc = doc_repo.get(document.id)
    assert published_doc.status == 'published'

    # --- Step 9: Delete the document (cascades sections) ---
    DomainEvent.handle(
        RemoveDocument,
        dependencies={'document_service': doc_repo},
        id=document.id,
    )
    assert doc_repo.exists(document.id) is False
    assert doc_repo.get_sections(document.id) == []

    # --- Step 10: Delete the folder (idempotent, no docs left) ---
    DomainEvent.handle(
        RemoveFolder,
        dependencies={
            'folder_service': folder_repo,
            'document_service': doc_repo,
        },
        id=folder.id,
    )
    assert folder_repo.exists(folder.id) is False


# ** test_int: embedding_workflow
def test_int_embedding_workflow(category_repo, doc_repo, template_repo):
    '''
    End-to-end test: create document → embed sections → search → remove → verify.
    '''

    # --- Step 1: Create a category and document with sections ---
    DomainEvent.handle(
        AddCategory,
        dependencies={'category_service': category_repo},
        id='tech-notes',
        name='Tech Notes',
    )

    document = DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': doc_repo},
        title='Embedding Test Doc',
        category_id='tech-notes',
    )

    sec_a = DomainEvent.handle(
        AddDocumentSection,
        dependencies={'document_service': doc_repo},
        document_id=document.id,
        title='Machine Learning Overview',
        content='ML is a subset of AI focused on learning from data.',
    )

    sec_b = DomainEvent.handle(
        AddDocumentSection,
        dependencies={'document_service': doc_repo},
        document_id=document.id,
        title='Database Indexing',
        content='B-tree indexes speed up read queries.',
    )

    sec_c = DomainEvent.handle(
        AddDocumentSection,
        dependencies={'document_service': doc_repo},
        document_id=document.id,
        title='Neural Networks',
        content='Neural networks are inspired by biological neurons.',
    )

    # --- Step 2: Embed all sections ---
    # Simulated embeddings: sec_a and sec_c are about ML (similar direction),
    # sec_b is about databases (orthogonal direction).
    embeddings = {
        sec_a.id: [0.9, 0.1, 0.0, 0.0],
        sec_b.id: [0.0, 0.0, 0.9, 0.1],
        sec_c.id: [0.8, 0.2, 0.0, 0.0],
    }

    count = DomainEvent.handle(
        EmbedDocumentSections,
        dependencies={'document_service': doc_repo},
        document_id=document.id,
        embeddings=embeddings,
        model_name='test-embedding-model',
    )
    assert count == 3

    # --- Step 3: Verify embeddings stored ---
    emb = doc_repo.get_embedding(sec_a.id)
    assert emb is not None
    assert len(emb) == 4

    # --- Step 4: Search with an ML-like query ---
    results = DomainEvent.handle(
        SearchSimilarSections,
        dependencies={'document_service': doc_repo},
        query_embedding=[1.0, 0.0, 0.0, 0.0],
        limit=3,
    )
    assert len(results) == 3
    # ML sections should rank higher than database section.
    ml_section_ids = {sec_a.id, sec_c.id}
    assert results[0]['section_id'] in ml_section_ids
    assert results[1]['section_id'] in ml_section_ids
    assert results[2]['section_id'] == sec_b.id

    # --- Step 5: Search with a DB-like query ---
    db_results = DomainEvent.handle(
        SearchSimilarSections,
        dependencies={'document_service': doc_repo},
        query_embedding=[0.0, 0.0, 1.0, 0.0],
        limit=1,
    )
    assert db_results[0]['section_id'] == sec_b.id

    # --- Step 6: Remove one embedding ---
    DomainEvent.handle(
        RemoveEmbedding,
        dependencies={'document_service': doc_repo},
        section_id=sec_c.id,
    )
    assert doc_repo.get_embedding(sec_c.id) is None
    # Other embeddings still exist.
    assert doc_repo.get_embedding(sec_a.id) is not None

    # --- Step 7: Search again — only 2 results now ---
    results_after = DomainEvent.handle(
        SearchSimilarSections,
        dependencies={'document_service': doc_repo},
        query_embedding=[1.0, 0.0, 0.0, 0.0],
        limit=5,
    )
    assert len(results_after) == 2
