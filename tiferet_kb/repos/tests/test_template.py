"""tiferet_kb Template H5 Repository Integration Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...mappers.template import TemplateAggregate, TemplateSectionAggregate
from ..template import TemplateH5Repository

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
