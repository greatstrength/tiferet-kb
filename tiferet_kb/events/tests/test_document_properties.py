"""tiferet_kb Document Property Event Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
import yaml

# ** app
from tiferet.assets import TiferetError
from tiferet.events import DomainEvent

from ...assets.error import (
    KB_DOCUMENT_NOT_FOUND_ID,
    KB_INVALID_DOCUMENT_ATTRIBUTE_ID,
    KB_INVALID_PROPERTY_FILTER_ID,
    KB_INVALID_PROPERTY_NAME_ID,
    KB_INVALID_PROPERTY_TYPE_ID,
    KB_INVALID_PROPERTY_VALUE_ID,
)
from ...domain.document import DocumentProperty, DocumentSection
from ...mappers.document import DocumentTableObject
from ...repos.document import DOCUMENT_PROPERTIES_TABLE, DocumentH5Repository
from ..document import (
    AddDocument,
    GetDocument,
    ListDocuments,
    RemoveDocument,
    RemoveDocumentProperty,
    SetDocumentProperty,
    UpdateDocument,
)
from ... import __version__

# *** fixtures

# ** fixture: doc_repo
@pytest.fixture
def doc_repo(tmp_path: Path) -> DocumentH5Repository:
    '''Provide a document repository on a temporary HDF5 file.'''
    return DocumentH5Repository(h5_file=str(tmp_path / 'props.h5'))

# *** functions

# ** function: add_doc
def add_doc(doc_repo: DocumentH5Repository, title: str, **kwargs):
    '''
    Create a document through the event.

    :param doc_repo: The document repository.
    :type doc_repo: DocumentH5Repository
    :param title: The document title.
    :type title: str
    :param kwargs: Optional header fields.
    :type kwargs: dict
    :return: The created document.
    '''

    # Persist through the event so the test uses the feature path.
    return DomainEvent.handle(
        AddDocument,
        dependencies={'document_service': doc_repo},
        title=title,
        **kwargs,
    )

# ** function: set_prop
def set_prop(doc_repo: DocumentH5Repository, document_id: str, name: str, value, value_type: str):
    '''
    Set one property through the event.

    :param doc_repo: The document repository.
    :type doc_repo: DocumentH5Repository
    :param document_id: The document identifier.
    :type document_id: str
    :param name: The property name.
    :type name: str
    :param value: The property value.
    :param value_type: The declared type.
    :type value_type: str
    :return: The stored property.
    '''

    # Persist through the event.
    return DomainEvent.handle(
        SetDocumentProperty,
        dependencies={'document_service': doc_repo},
        document_id=document_id,
        name=name,
        value=value,
        value_type=value_type,
    )

# ** function: error_code
def error_code(exc_info) -> str:
    '''
    Return the structured error code from a raised TiferetError.

    :param exc_info: The pytest exception info.
    :return: The error code.
    :rtype: str
    '''

    # Return the asset code.
    return exc_info.value.error_code

# *** tests

# ** test: set_and_get_number_then_replace_with_string
def test_set_and_get_number_then_replace_with_string(doc_repo):
    '''A set stores one typed value, and a second set of that name replaces it.'''

    doc = add_doc(doc_repo, 'Notes')
    set_prop(doc_repo, doc.id, 'priority', 1, 'number')

    loaded = DomainEvent.handle(
        GetDocument,
        dependencies={'document_service': doc_repo},
        id=doc.id,
    )
    assert len(loaded.properties) == 1
    assert loaded.properties[0].name == 'priority'
    assert loaded.properties[0].value == 1
    assert loaded.properties[0].value_type == 'number'

    set_prop(doc_repo, doc.id, 'priority', 'high', 'string')
    replaced = doc_repo.get(doc.id)
    assert len(replaced.properties) == 1
    assert replaced.properties[0].value == 'high'
    assert replaced.properties[0].value_type == 'string'

# ** test: get_without_a_property_table_is_an_empty_bag
def test_get_without_a_property_table_is_an_empty_bag(doc_repo):
    '''get returns [] when the document has no properties and when the table is absent.'''

    doc = add_doc(doc_repo, 'Empty')
    loaded = doc_repo.get(doc.id)
    assert loaded.properties == []

    with doc_repo.client() as h5:
        assert not h5.node_exists(DOCUMENT_PROPERTIES_TABLE)

# ** test: set_on_missing_document_writes_no_row
def test_set_on_missing_document_writes_no_row(doc_repo):
    '''A set on a missing document raises and does not create a property row.'''

    with pytest.raises(TiferetError) as exc_info:
        set_prop(doc_repo, 'missing', 'priority', 1, 'number')
    assert error_code(exc_info) == KB_DOCUMENT_NOT_FOUND_ID

    if doc_repo.file_exists():
        with doc_repo.client() as h5:
            assert not h5.node_exists(DOCUMENT_PROPERTIES_TABLE)

# ** test: invalid_name_type_and_value_are_refused
def test_invalid_name_type_and_value_are_refused(doc_repo):
    '''The event raises the asset codes, and the domain object refuses the same values.'''

    doc = add_doc(doc_repo, 'Rules')
    cases = [
        ('', 1, 'number', KB_INVALID_PROPERTY_NAME_ID),
        ('   ', 1, 'number', KB_INVALID_PROPERTY_NAME_ID),
        ('priority', 1, 'int', KB_INVALID_PROPERTY_TYPE_ID),
        ('priority', 1, 'str', KB_INVALID_PROPERTY_TYPE_ID),
        ('priority', True, 'bool', KB_INVALID_PROPERTY_TYPE_ID),
        ('priority', True, 'number', KB_INVALID_PROPERTY_VALUE_ID),
        ('priority', 1, 'boolean', KB_INVALID_PROPERTY_VALUE_ID),
        ('priority', 'true', 'boolean', KB_INVALID_PROPERTY_VALUE_ID),
        ('priority', None, 'string', KB_INVALID_PROPERTY_VALUE_ID),
        ('priority', float('nan'), 'number', KB_INVALID_PROPERTY_VALUE_ID),
        ('priority', float('inf'), 'number', KB_INVALID_PROPERTY_VALUE_ID),
    ]
    for name, value, value_type, code in cases:
        with pytest.raises(TiferetError) as exc_info:
            set_prop(doc_repo, doc.id, name, value, value_type)
        assert error_code(exc_info) == code
        with pytest.raises(Exception):
            DocumentProperty(
                document_id=doc.id,
                name=name,
                value=value,
                value_type=value_type,
            )

    stored = set_prop(doc_repo, doc.id, 'note', '', 'string')
    assert stored.value == ''
    assert doc_repo.get(doc.id).properties[0].value == ''

# ** test: names_are_stripped_once_and_do_not_alias_status
def test_names_are_stripped_once_and_do_not_alias_status(doc_repo):
    '''Strip collapses one name. Case stays. A property named status is not the header.'''

    doc = add_doc(doc_repo, 'Names', status='draft')
    set_prop(doc_repo, doc.id, ' priority ', 1, 'number')
    set_prop(doc_repo, doc.id, 'priority', 2, 'number')
    set_prop(doc_repo, doc.id, 'Priority', 'other', 'string')
    set_prop(doc_repo, doc.id, 'status', 'published', 'string')

    loaded = doc_repo.get(doc.id)
    by_name = {prop.name: prop for prop in loaded.properties}
    assert set(by_name) == {'priority', 'Priority', 'status'}
    assert by_name['priority'].value == 2
    assert loaded.status == 'draft'

# ** test: remove_is_idempotent_and_only_a_real_remove_moves_the_clock
def test_remove_is_idempotent_and_only_a_real_remove_moves_the_clock(doc_repo):
    '''Set moves updated_at. A second remove, or a missing document, does not raise or move it.'''

    doc = add_doc(doc_repo, 'Clock')
    before = doc_repo.get(doc.id).updated_at
    set_prop(doc_repo, doc.id, 'priority', 1, 'number')
    after_set = doc_repo.get(doc.id).updated_at
    assert after_set != before

    DomainEvent.handle(
        RemoveDocumentProperty,
        dependencies={'document_service': doc_repo},
        document_id=doc.id,
        name='priority',
    )
    after_remove = doc_repo.get(doc.id).updated_at
    assert after_remove != after_set
    assert doc_repo.get(doc.id).properties == []

    DomainEvent.handle(
        RemoveDocumentProperty,
        dependencies={'document_service': doc_repo},
        document_id=doc.id,
        name='priority',
    )
    assert doc_repo.get(doc.id).updated_at == after_remove

    returned = DomainEvent.handle(
        RemoveDocumentProperty,
        dependencies={'document_service': doc_repo},
        document_id='missing-doc',
        name='priority',
    )
    assert returned == 'priority'

# ** test: header_updates_do_not_drop_or_alias_the_bag
def test_header_updates_do_not_drop_or_alias_the_bag(doc_repo):
    '''UpdateDocument rejects property attributes, and a title or folder change keeps the bag.'''

    doc = add_doc(doc_repo, 'Header')
    set_prop(doc_repo, doc.id, 'priority', 'high', 'string')

    for attribute in ('properties', 'priority'):
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                UpdateDocument,
                dependencies={'document_service': doc_repo},
                id=doc.id,
                attribute=attribute,
                value='nope',
            )
        assert error_code(exc_info) == KB_INVALID_DOCUMENT_ATTRIBUTE_ID

    DomainEvent.handle(
        UpdateDocument,
        dependencies={'document_service': doc_repo},
        id=doc.id,
        attribute='title',
        value='Renamed',
    )
    DomainEvent.handle(
        UpdateDocument,
        dependencies={'document_service': doc_repo},
        id=doc.id,
        attribute='folder_id',
        value='folder-1',
    )
    loaded = doc_repo.get(doc.id)
    assert loaded.title == 'Renamed'
    assert loaded.folder_id == 'folder-1'
    assert loaded.properties[0].name == 'priority'
    assert loaded.properties[0].value == 'high'

# ** test: list_include_and_filter_are_independent
def test_list_include_and_filter_are_independent(doc_repo):
    '''list loads the bag only when asked, and one property filter AND-s with header filters.'''

    draft = add_doc(doc_repo, 'Draft', folder_id='folder-1', status='draft')
    other = add_doc(doc_repo, 'Other', folder_id='folder-2', status='published')
    set_prop(doc_repo, draft.id, 'zeta', 1, 'number')
    set_prop(doc_repo, draft.id, 'alpha', False, 'boolean')
    set_prop(doc_repo, other.id, 'priority', 'high', 'string')

    headers = DomainEvent.handle(
        ListDocuments,
        dependencies={'document_service': doc_repo},
    )
    assert all(doc.properties == [] for doc in headers)

    included = doc_repo.list(include_properties=True)
    by_id = {doc.id: doc for doc in included}
    assert [prop.name for prop in by_id[draft.id].properties] == ['alpha', 'zeta']
    assert by_id[other.id].properties[0].value == 'high'
    assert by_id[draft.id].sections == []

    matched = doc_repo.list(
        property_name='priority',
        property_value='high',
        property_value_type='string',
    )
    assert [doc.id for doc in matched] == [other.id]
    assert matched[0].properties == []

    number_miss = doc_repo.list(
        property_name='priority',
        property_value=1,
        property_value_type='number',
    )
    assert number_miss == []

    false_miss = doc_repo.list(
        property_name='alpha',
        property_value=False,
        property_value_type='boolean',
    )
    assert [doc.id for doc in false_miss] == [draft.id]
    zero_miss = doc_repo.list(
        property_name='alpha',
        property_value=0,
        property_value_type='number',
    )
    assert zero_miss == []

    combined = doc_repo.list(
        folder_id='folder-1',
        status='draft',
        property_name='zeta',
        property_value=1,
        property_value_type='number',
    )
    assert [doc.id for doc in combined] == [draft.id]
    missed = doc_repo.list(
        folder_id='folder-2',
        property_name='zeta',
        property_value=1,
        property_value_type='number',
    )
    assert missed == []

# ** test: quoted_filter_matches_only_the_stored_value
def test_quoted_filter_matches_only_the_stored_value(doc_repo):
    '''A quote, colon, or backslash matches only the stored row and does not list the file.'''

    quoted = add_doc(doc_repo, 'Quoted')
    plain = add_doc(doc_repo, 'Plain')
    name = 'say"hi:there\\x'
    value = 'a"b:c\\d'
    set_prop(doc_repo, quoted.id, name, value, 'string')
    set_prop(doc_repo, plain.id, 'priority', 'high', 'string')

    matched = doc_repo.list(
        property_name=name,
        property_value=value,
        property_value_type='string',
    )
    assert [doc.id for doc in matched] == [quoted.id]

    none = doc_repo.list(
        property_name='no"such',
        property_value='value"with:colon\\slash',
        property_value_type='string',
    )
    assert none == []

    with pytest.raises(TiferetError) as exc_info:
        doc_repo.list(property_name='priority', property_value='high')
    assert error_code(exc_info) == KB_INVALID_PROPERTY_FILTER_ID

# ** test: list_event_forwards_property_arguments
def test_list_event_forwards_property_arguments(doc_repo):
    '''ListDocuments forwards the property arguments, including the defaults.'''

    add_doc(doc_repo, 'Forward')
    seen = {}
    original = doc_repo.list

    def capture(**kwargs):
        seen.update(kwargs)
        return original(**kwargs)

    doc_repo.list = capture
    DomainEvent.handle(
        ListDocuments,
        dependencies={'document_service': doc_repo},
    )
    assert seen == {
        'folder_id': None,
        'category_id': None,
        'status': None,
        'title': None,
        'include_properties': False,
        'property_name': None,
        'property_value': None,
        'property_value_type': None,
    }
    assert 'include_sections' not in seen

    DomainEvent.handle(
        ListDocuments,
        dependencies={'document_service': doc_repo},
        include_properties=True,
        property_name='priority',
        property_value=False,
        property_value_type='boolean',
    )
    assert seen['include_properties'] is True
    assert seen['property_value'] is False

# ** test: delete_drops_rows_and_does_not_remove_the_table_node
def test_delete_drops_rows_and_does_not_remove_the_table_node(doc_repo):
    '''Deleting a document removes its property rows through the table, not remove_node.'''

    doc = add_doc(doc_repo, 'Gone', id='same-id')
    set_prop(doc_repo, doc.id, 'priority', 'high', 'string')
    calls = []
    original = doc_repo.node_repo.remove_node

    def wrapped(h5, path, recursive=False):
        calls.append(path)
        return original(h5, path, recursive=recursive)

    doc_repo.node_repo.remove_node = wrapped
    DomainEvent.handle(
        RemoveDocument,
        dependencies={'document_service': doc_repo},
        id=doc.id,
    )
    assert DOCUMENT_PROPERTIES_TABLE not in calls

    with doc_repo.client() as h5:
        assert h5.node_exists(DOCUMENT_PROPERTIES_TABLE)
        rows = h5.read_rows(
            DOCUMENT_PROPERTIES_TABLE,
            condition=f'(document_id == b"same-id")',
        )
        assert rows == []

    reborn = add_doc(doc_repo, 'Again', id='same-id')
    assert doc_repo.get(reborn.id).properties == []
    assert doc_repo.list(
        property_name='priority',
        property_value='high',
        property_value_type='string',
    ) == []

# ** test: header_columns_and_wiring_stay_in_scope
def test_header_columns_and_wiring_stay_in_scope():
    '''The header columns, section model, version, and feature wiring match the proposal.'''

    assert set(DocumentTableObject._H5_TYPES) == {
        'id',
        'title',
        'category_id',
        'template_id',
        'folder_id',
        'status',
        'created_at',
        'updated_at',
    }
    assert 'content' not in DocumentSection.model_fields
    assert __version__ == '1.0.0a1'

    root = Path(__file__).resolve().parents[3]
    feature = yaml.safe_load((root / 'app/configs/feature.yml').read_text())
    document = feature['features']['document']
    assert 'set_property' in document
    assert 'remove_property' in document
    assert document['set_property']['commands'][0]['attribute_id'] == 'set_document_property_event'
    container = yaml.safe_load((root / 'app/configs/container.yml').read_text())
    assert container['attrs']['set_document_property_event']['class_name'] == 'SetDocumentProperty'
    assert container['attrs']['remove_document_property_event']['class_name'] == 'RemoveDocumentProperty'
