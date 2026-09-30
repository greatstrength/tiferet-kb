"""tiferet_kb Tagging Workflow Integration Tests"""

# *** imports

# ** infra
import pytest
from tiferet.assets import TiferetError
from tiferet.events import DomainEvent

# ** app
from ..assets import errors as err
from ..events import (
    AddDocument,
    AddDocumentSection,
    AddTag,
    AddTemplate,
    ApplyTemplate,
    GetDocument,
    GetTag,
    ListDocumentTags,
    ListDocuments,
    ListTags,
    RemoveDocument,
    RemoveTag,
    TagDocument,
    UntagDocument,
    UpdateDocument,
    UpdateTag,
)
from ..repos.document import DocumentH5Repository
from ..repos.tag import TagH5Repository
from ..repos.template import TemplateH5Repository

# *** fixtures

# ** fixture: h5_file
@pytest.fixture
def h5_file(tmp_path) -> str:
    '''Provide a single temporary HDF5 file for the tag and document repos.'''
    return str(tmp_path / 'kb.h5')

# ** fixture: doc_repo
@pytest.fixture
def doc_repo(h5_file) -> DocumentH5Repository:
    '''Document repository.'''
    return DocumentH5Repository(h5_file=h5_file)

# ** fixture: tag_repo
@pytest.fixture
def tag_repo(h5_file) -> TagH5Repository:
    '''Tag repository.'''
    return TagH5Repository(h5_file=h5_file)

# ** fixture: template_repo
@pytest.fixture
def template_repo(h5_file) -> TemplateH5Repository:
    '''Template repository.'''
    return TemplateH5Repository(h5_file=h5_file)

# ** fixture: deps
@pytest.fixture
def deps(doc_repo, tag_repo) -> dict:
    '''Event dependencies shared by the tagging workflow.'''
    return {
        'document_service': doc_repo,
        'tag_service': tag_repo,
    }

# *** tests

# ** test_int: tagging_acceptance
def test_int_tagging_acceptance(doc_repo, tag_repo, template_repo, deps):
    '''
    Tags are many-to-many labels, listed by association, and cleaned up with the document.
    '''

    # Create two tags. Color may be omitted. The id is stored as given.
    release = DomainEvent.handle(
        AddTag,
        dependencies={'tag_service': tag_repo},
        id='My-Tag',
        name='Release',
    )
    assert release.color is None
    ship = DomainEvent.handle(
        AddTag,
        dependencies={'tag_service': tag_repo},
        id='ship',
        name='Release',
        color='blue',
    )
    fetched = DomainEvent.handle(
        GetTag,
        dependencies={'tag_service': tag_repo},
        id='My-Tag',
    )
    assert fetched.name == 'Release'
    assert fetched.color is None
    listed = DomainEvent.handle(ListTags, dependencies={'tag_service': tag_repo})
    assert {tag.id for tag in listed} == {'My-Tag', 'ship'}

    # A second add of the same id fails. An unknown get fails.
    with pytest.raises(TiferetError) as duplicate:
        DomainEvent.handle(
            AddTag,
            dependencies={'tag_service': tag_repo},
            id='My-Tag',
            name='Other',
        )
    assert duplicate.value.error_code == err.KB_TAG_ALREADY_EXISTS_ID
    with pytest.raises(TiferetError) as missing:
        DomainEvent.handle(
            GetTag,
            dependencies={'tag_service': tag_repo},
            id='nope',
        )
    assert missing.value.error_code == err.KB_TAG_NOT_FOUND_ID

    # Rename, recolor, and clear color. Other attributes, including id, are rejected.
    DomainEvent.handle(
        UpdateTag,
        dependencies={'tag_service': tag_repo},
        id='ship',
        attribute='name',
        value='Ship',
    )
    DomainEvent.handle(
        UpdateTag,
        dependencies={'tag_service': tag_repo},
        id='ship',
        attribute='color',
        value='#111111',
    )
    cleared = DomainEvent.handle(
        UpdateTag,
        dependencies={'tag_service': tag_repo},
        id='ship',
        attribute='color',
        value=None,
    )
    assert cleared.name == 'Ship'
    assert cleared.color is None
    with pytest.raises(TiferetError) as invalid:
        DomainEvent.handle(
            UpdateTag,
            dependencies={'tag_service': tag_repo},
            id='ship',
            attribute='id',
            value='other',
        )
    assert invalid.value.error_code == err.KB_INVALID_TAG_ATTRIBUTE_ID

    # Two documents, one of them categorized and filed, plus a section on the tagged one.
    notes = DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': doc_repo},
        title='Notes',
        id='doc-notes',
        category_id='meeting-notes',
        folder_id='folder-1',
        status='draft',
    )
    other = DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': doc_repo},
        title='Other',
        id='doc-other',
        folder_id='folder-2',
        status='published',
    )
    DomainEvent.handle(
        AddDocumentSection,
        dependencies={'document_service': doc_repo},
        document_id=notes.id,
        title='Body',
        content='A passage.',
    )

    # Missing document and missing tag write no association.
    with pytest.raises(TiferetError) as no_doc:
        DomainEvent.handle(
            TagDocument,
            dependencies=deps,
            document_id='missing',
            tag_id='My-Tag',
        )
    assert no_doc.value.error_code == err.KB_DOCUMENT_NOT_FOUND_ID
    assert tag_repo.list_document_ids('My-Tag') == []
    with pytest.raises(TiferetError) as no_tag:
        DomainEvent.handle(
            TagDocument,
            dependencies=deps,
            document_id=notes.id,
            tag_id='missing',
        )
    assert no_tag.value.error_code == err.KB_TAG_NOT_FOUND_ID
    assert tag_repo.list_document_ids('missing') == []

    # One document carries two tags. One tag is carried by two documents. A repeat is one row.
    DomainEvent.handle(TagDocument, dependencies=deps, document_id=notes.id, tag_id='My-Tag')
    DomainEvent.handle(TagDocument, dependencies=deps, document_id=notes.id, tag_id='My-Tag')
    DomainEvent.handle(TagDocument, dependencies=deps, document_id=notes.id, tag_id='ship')
    DomainEvent.handle(TagDocument, dependencies=deps, document_id=other.id, tag_id='My-Tag')
    assert tag_repo.list_document_ids('My-Tag') == [notes.id, other.id]
    carried = {tag.id for tag in DomainEvent.handle(
        ListDocumentTags,
        dependencies=deps,
        document_id=notes.id,
    )}
    assert carried == {'My-Tag', 'ship'}

    # Tagging does not write category_id. UpdateDocument still rejects tag attributes.
    assert doc_repo.get(notes.id).category_id == 'meeting-notes'
    for attribute in ('tag_id', 'tags'):
        with pytest.raises(TiferetError) as bad_attr:
            DomainEvent.handle(
                UpdateDocument,
                dependencies={'document_service': doc_repo},
                id=notes.id,
                attribute=attribute,
                value='My-Tag',
            )
        assert bad_attr.value.error_code == err.KB_INVALID_DOCUMENT_ATTRIBUTE_ID

    # tag_id intersects header filters and returns headers, not sections.
    tagged = DomainEvent.handle(
        ListDocuments,
        dependencies=deps,
        tag_id='My-Tag',
    )
    assert [doc.id for doc in tagged] == [notes.id, other.id]
    assert all(doc.sections == [] for doc in tagged)
    narrowed = DomainEvent.handle(
        ListDocuments,
        dependencies=deps,
        tag_id='My-Tag',
        folder_id='folder-1',
        category_id='meeting-notes',
        status='draft',
    )
    assert [doc.id for doc in narrowed] == [notes.id]
    unfiltered = DomainEvent.handle(ListDocuments, dependencies=deps)
    assert {doc.id for doc in unfiltered} == {notes.id, other.id}
    assert DomainEvent.handle(
        ListDocuments,
        dependencies=deps,
        tag_id='no-such-tag',
    ) == []

    # An existing untagged document lists no tags. A missing document does not.
    fresh = DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': doc_repo},
        title='Fresh',
        id='doc-fresh',
    )
    assert DomainEvent.handle(
        ListDocumentTags,
        dependencies=deps,
        document_id=fresh.id,
    ) == []
    with pytest.raises(TiferetError) as no_list:
        DomainEvent.handle(
            ListDocumentTags,
            dependencies=deps,
            document_id='missing',
        )
    assert no_list.value.error_code == err.KB_DOCUMENT_NOT_FOUND_ID

    # RemoveTag refuses while a document carries the tag, and the label remains.
    with pytest.raises(TiferetError) as in_use:
        DomainEvent.handle(
            RemoveTag,
            dependencies={'tag_service': tag_repo},
            id='ship',
        )
    assert in_use.value.error_code == err.KB_TAG_IN_USE_ID
    assert tag_repo.exists('ship') is True

    # Untag is idempotent. After the only carrier is untagged, RemoveTag deletes the label.
    DomainEvent.handle(
        UntagDocument,
        dependencies={'tag_service': tag_repo},
        document_id=notes.id,
        tag_id='ship',
    )
    DomainEvent.handle(
        UntagDocument,
        dependencies={'tag_service': tag_repo},
        document_id=notes.id,
        tag_id='ship',
    )
    DomainEvent.handle(
        UntagDocument,
        dependencies={'tag_service': tag_repo},
        document_id=fresh.id,
        tag_id='never',
    )
    assert tag_repo.list_document_ids('ship') == []
    assert DomainEvent.handle(
        RemoveTag,
        dependencies={'tag_service': tag_repo},
        id='ship',
    ) == 'ship'
    assert tag_repo.exists('ship') is False
    assert DomainEvent.handle(
        RemoveTag,
        dependencies={'tag_service': tag_repo},
        id='ship',
    ) == 'ship'

    # Removing the only remaining carrier document lets RemoveTag succeed.
    DomainEvent.handle(RemoveDocument, dependencies=deps, id=other.id)
    assert tag_repo.list_document_ids('My-Tag') == [notes.id]
    DomainEvent.handle(RemoveDocument, dependencies=deps, id=notes.id)
    assert tag_repo.list_document_ids('My-Tag') == []
    assert DomainEvent.handle(
        RemoveTag,
        dependencies={'tag_service': tag_repo},
        id='My-Tag',
    ) == 'My-Tag'

    # ApplyTemplate copies the suggested category and stamps no tags.
    DomainEvent.handle(
        AddTemplate,
        dependencies={'template_service': template_repo},
        name='Outline',
        category_id='meeting-notes',
        sections=[{'title': 'Start', 'content_type': 'markdown', 'default_content': 'Hi'}],
    )
    template = template_repo.list()[0]
    stamped = DomainEvent.handle(
        ApplyTemplate,
        dependencies={
            'template_service': template_repo,
            'document_service': doc_repo,
        },
        template_id=template.id,
        title='From template',
    )
    assert stamped.category_id == 'meeting-notes'
    assert DomainEvent.handle(
        ListDocumentTags,
        dependencies=deps,
        document_id=stamped.id,
    ) == []
    loaded = DomainEvent.handle(
        GetDocument,
        dependencies={'document_service': doc_repo},
        id=stamped.id,
    )
    assert not hasattr(loaded, 'tags') or 'tags' not in type(loaded).model_fields
    assert loaded.sections
