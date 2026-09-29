"""tiferet_kb Template H5 Repository Integration Tests"""

# *** imports

# ** core
import os

# ** infra
import pytest
import tables
from tiferet.interfaces import ServiceError
from tiferet_h5.repos import NodeRepository, TableRepository
from tiferet_h5.utils import H5Client

# ** app
from ...mappers.template import (
    TemplateAggregate,
    TemplateSectionAggregate,
    TemplateSectionTableObject,
    TemplateTableObject,
)
from ...utils.h5 import remove_node
from ..template import (
    TEMPLATE_SECTIONS_TABLE,
    TEMPLATES_TABLE,
    TemplateH5Repository,
    TemplateSectionTableRepository,
    TemplateTableRepository,
)

# *** fixtures

# ** fixture: h5_file
@pytest.fixture
def h5_file(tmp_path) -> str:
    '''Provide a temporary HDF5 file path.'''
    return str(tmp_path / 'test_kb.h5')


# ** fixture: tmpl_repo
@pytest.fixture
def tmpl_repo(h5_file: str) -> TemplateH5Repository:
    '''Provide a TemplateH5Repository backed by a temporary HDF5 file.'''
    return TemplateH5Repository(h5_file=h5_file)


# ** fixture: sample_template
@pytest.fixture
def sample_template() -> TemplateAggregate:
    '''Provide a sample TemplateAggregate.'''
    return TemplateAggregate(
        id='tmpl-001',
        name='Meeting Notes',
        description='For meetings',
        category_id='meetings',
    )


# ** fixture: sample_section
@pytest.fixture
def sample_section() -> TemplateSectionAggregate:
    '''Provide a sample TemplateSectionAggregate.'''
    return TemplateSectionAggregate(
        id='tsec-001',
        template_id='tmpl-001',
        title='Agenda',
        content_type='markdown',
        default_content='## Agenda',
        position=0,
    )

# *** tests

# ** test_int: save_and_exists
def test_int_save_and_exists(tmpl_repo, sample_template):
    '''Test that saving a template makes it exist.'''

    tmpl_repo.save(sample_template)
    assert tmpl_repo.exists('tmpl-001') is True


# ** test_int: exists_negative
def test_int_exists_negative(tmpl_repo, sample_template):
    '''Test that exists returns False for non-existent.'''

    tmpl_repo.save(sample_template)
    assert tmpl_repo.exists('nonexistent') is False


# ** test_int: get_success
def test_int_get_success(tmpl_repo, sample_template):
    '''Test successful retrieval.'''

    tmpl_repo.save(sample_template)
    result = tmpl_repo.get('tmpl-001')

    assert result is not None
    assert result.id == 'tmpl-001'
    assert result.name == 'Meeting Notes'
    assert result.category_id == 'meetings'


# ** test_int: get_with_sections
def test_int_get_with_sections(tmpl_repo, sample_template, sample_section):
    '''Test that get() returns template with sections populated.'''

    tmpl_repo.save(sample_template)
    tmpl_repo.save_section(sample_section)

    result = tmpl_repo.get('tmpl-001')
    assert len(result.sections) == 1
    assert result.sections[0].title == 'Agenda'


# ** test_int: get_not_found
def test_int_get_not_found(tmpl_repo, sample_template):
    '''Test that get returns None for non-existent.'''

    tmpl_repo.save(sample_template)
    assert tmpl_repo.get('nonexistent') is None


# ** test_int: list_all
def test_int_list_all(tmpl_repo):
    '''Test listing all templates.'''

    tmpl_repo.save(TemplateAggregate(id='t1', name='Template 1'))
    tmpl_repo.save(TemplateAggregate(id='t2', name='Template 2'))

    result = tmpl_repo.list()
    assert len(result) == 2


# ** test_int: list_by_category
def test_int_list_by_category(tmpl_repo):
    '''Test listing templates filtered by category.'''

    tmpl_repo.save(TemplateAggregate(id='t1', name='T1', category_id='meetings'))
    tmpl_repo.save(TemplateAggregate(id='t2', name='T2', category_id='design'))

    result = tmpl_repo.list(category_id='meetings')
    assert len(result) == 1
    assert result[0].id == 't1'


# ** test_int: list_empty
def test_int_list_empty(tmpl_repo):
    '''Test listing when no templates exist.'''

    assert tmpl_repo.list() == []


# ** test_int: save_upsert
def test_int_save_upsert(tmpl_repo, sample_template):
    '''Test that saving an existing template updates it.'''

    tmpl_repo.save(sample_template)
    sample_template.rename('Updated Name')
    tmpl_repo.save(sample_template)

    result = tmpl_repo.get('tmpl-001')
    assert result.name == 'Updated Name'
    assert len(tmpl_repo.list()) == 1


# ** test_int: delete_cascades
def test_int_delete_cascades(tmpl_repo, sample_template, sample_section):
    '''Test that deleting a template cascades to its sections.'''

    tmpl_repo.save(sample_template)
    tmpl_repo.save_section(sample_section)

    tmpl_repo.delete('tmpl-001')
    assert tmpl_repo.exists('tmpl-001') is False


# ** test_int: delete_idempotent
def test_int_delete_idempotent(tmpl_repo, sample_template):
    '''Test that deleting a non-existent template is idempotent.'''

    tmpl_repo.save(sample_template)
    tmpl_repo.delete('nonexistent')  # Should not raise


# ** test_int: save_section_upsert
def test_int_save_section_upsert(tmpl_repo, sample_template, sample_section):
    '''Test that save_section upserts.'''

    tmpl_repo.save(sample_template)
    tmpl_repo.save_section(sample_section)

    sample_section.set_default_content('Updated agenda')
    tmpl_repo.save_section(sample_section)

    result = tmpl_repo.get('tmpl-001')
    assert len(result.sections) == 1
    assert result.sections[0].default_content == 'Updated agenda'


# *** tests: RFP-001 storage alignment

# ** test_int: inherits_neither_mixin
def test_int_inherits_neither_mixin():
    '''The service repository inherits no mixin; each collaborator inherits TableRepository only.'''

    assert not issubclass(TemplateH5Repository, TableRepository)
    assert not issubclass(TemplateH5Repository, NodeRepository)
    for collaborator in (TemplateTableRepository, TemplateSectionTableRepository):
        assert issubclass(collaborator, TableRepository)
        assert not issubclass(collaborator, NodeRepository)
    assert TemplateTableRepository.table_path == TEMPLATES_TABLE
    assert TemplateSectionTableRepository.table_path == TEMPLATE_SECTIONS_TABLE


# ** test_int: second_save_leaves_one_header_row
def test_int_second_save_leaves_one_header_row(tmpl_repo, h5_file, sample_template):
    '''Saving the same template id twice leaves a single header row.'''

    tmpl_repo.save(sample_template)
    sample_template.rename('Renamed')
    tmpl_repo.save(sample_template)

    with H5Client(path=h5_file, mode='r') as h5:
        rows = h5.read_rows(TEMPLATES_TABLE)
    assert len(rows) == 1
    assert tmpl_repo.get('tmpl-001').name == 'Renamed'


# ** test_int: tables_are_stamped_on_first_create
def test_int_tables_are_stamped_on_first_create(tmpl_repo, h5_file, sample_template, sample_section):
    '''Both template tables carry their class fingerprint, and a later save does not rewrite it.'''

    tmpl_repo.save(sample_template)
    tmpl_repo.save_section(sample_section)

    with H5Client(path=h5_file, mode='a') as h5:
        assert h5.get_node_attr(TEMPLATES_TABLE, 'schema_version') == TemplateTableObject.schema_fingerprint()
        assert h5.get_node_attr(TEMPLATE_SECTIONS_TABLE, 'schema_version') == TemplateSectionTableObject.schema_fingerprint()
        h5.set_node_attr(TEMPLATES_TABLE, 'schema_version', 'sentinel')

    tmpl_repo.save(sample_template)

    with H5Client(path=h5_file, mode='r') as h5:
        assert h5.get_node_attr(TEMPLATES_TABLE, 'schema_version') == 'sentinel'


# ** test_int: verify_passes_and_detects_drift
def test_int_verify_passes_and_detects_drift(tmpl_repo, h5_file, sample_template, sample_section):
    '''verify passes on fresh tables and raises H5_SCHEMA_MISMATCH after a width change.'''

    tmpl_repo.save(sample_template)
    tmpl_repo.save_section(sample_section)
    tmpl_repo.verify()

    # Replace the header table with a narrower name column.
    narrow = type(
        'NarrowTemplateDescription',
        (tables.IsDescription,),
        {**TemplateTableObject._H5_TYPES, 'name': tables.StringCol(8)},
    )
    with H5Client(path=h5_file, mode='a') as h5:
        remove_node(h5, TEMPLATES_TABLE)
        h5.create_table(TEMPLATES_TABLE, narrow)

    with pytest.raises(ServiceError) as exc_info:
        tmpl_repo.verify()
    assert exc_info.value.error_code == 'H5_SCHEMA_MISMATCH'


# ** test_int: unstamped_file_still_opens
def test_int_unstamped_file_still_opens(tmpl_repo, h5_file, sample_template):
    '''A file written without schema_version still lists and verifies, and reads do not stamp it.'''

    with H5Client(path=h5_file, mode='a') as h5:
        t = h5.create_table(TEMPLATES_TABLE, TemplateTableObject.get_description())
        TemplateTableObject.from_model(sample_template).to_row(t)
        t.flush()

    assert [t.id for t in tmpl_repo.list()] == ['tmpl-001']
    assert tmpl_repo.exists('tmpl-001') is True
    tmpl_repo.verify()

    with H5Client(path=h5_file, mode='r') as h5:
        assert 'schema_version' not in h5.get_node_attrs(TEMPLATES_TABLE)


# ** test_int: missing_file_reads_are_empty_and_not_created
def test_int_missing_file_reads_are_empty_and_not_created(tmpl_repo, h5_file):
    '''Reads, delete, and verify on a missing file do not create the file.'''

    assert tmpl_repo.get('nope') is None
    assert tmpl_repo.exists('nope') is False
    assert tmpl_repo.list() == []
    tmpl_repo.delete('nope')
    tmpl_repo.verify()

    assert not os.path.exists(h5_file)
