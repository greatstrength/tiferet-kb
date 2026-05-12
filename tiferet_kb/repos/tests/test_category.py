"""tiferet_kb Category H5 Repository Integration Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...mappers import CategoryAggregate
from ..category import CategoryH5Repository

# *** fixtures

# ** fixture: h5_file
@pytest.fixture
def h5_file(tmp_path) -> str:
    '''
    Provide a temporary HDF5 file path.
    '''
    return str(tmp_path / 'test_kb.h5')


# ** fixture: category_repo
@pytest.fixture
def category_repo(h5_file: str) -> CategoryH5Repository:
    '''
    Provide a CategoryH5Repository backed by a temporary HDF5 file.
    '''
    return CategoryH5Repository(h5_file=h5_file)


# ** fixture: sample_category
@pytest.fixture
def sample_category() -> CategoryAggregate:
    '''
    Provide a sample CategoryAggregate for testing.
    '''
    return CategoryAggregate(
        id='meeting-notes',
        name='Meeting Notes',
        description='Notes from meetings',
        icon='📝',
        color='#3B82F6',
    )

# *** tests

# ** test_int: save_and_exists
def test_int_save_and_exists(category_repo: CategoryH5Repository, sample_category: CategoryAggregate):
    '''
    Test that saving a category makes it exist.
    '''

    # Save the category.
    category_repo.save(sample_category)

    # Assert the category now exists.
    assert category_repo.exists('meeting-notes') is True


# ** test_int: exists_negative
def test_int_exists_negative(category_repo: CategoryH5Repository, sample_category: CategoryAggregate):
    '''
    Test that exists returns False for a non-existent category.
    '''

    # Save a category to create the file structure.
    category_repo.save(sample_category)

    # Assert a different category does not exist.
    assert category_repo.exists('nonexistent') is False


# ** test_int: get_success
def test_int_get_success(category_repo: CategoryH5Repository, sample_category: CategoryAggregate):
    '''
    Test successful retrieval of a saved category.
    '''

    # Save and retrieve the category.
    category_repo.save(sample_category)
    result = category_repo.get('meeting-notes')

    # Assert the retrieved category matches.
    assert result is not None
    assert result.id == 'meeting-notes'
    assert result.name == 'Meeting Notes'
    assert result.description == 'Notes from meetings'
    assert result.icon == '📝'
    assert result.color == '#3B82F6'


# ** test_int: get_not_found
def test_int_get_not_found(category_repo: CategoryH5Repository, sample_category: CategoryAggregate):
    '''
    Test that get returns None for a non-existent category.
    '''

    # Save a category to create the file structure.
    category_repo.save(sample_category)

    # Assert None is returned for a missing category.
    assert category_repo.get('nonexistent') is None


# ** test_int: list_categories
def test_int_list_categories(category_repo: CategoryH5Repository):
    '''
    Test listing all categories.
    '''

    # Save two categories.
    category_repo.save(CategoryAggregate(id='meeting-notes', name='Meeting Notes'))
    category_repo.save(CategoryAggregate(id='design-docs', name='Design Docs'))

    # List all categories.
    result = category_repo.list()

    # Assert both categories are returned.
    assert len(result) == 2
    ids = {c.id for c in result}
    assert 'meeting-notes' in ids
    assert 'design-docs' in ids


# ** test_int: list_empty
def test_int_list_empty(category_repo: CategoryH5Repository, sample_category: CategoryAggregate):
    '''
    Test listing categories when the root group does not exist.
    '''

    # Save and delete to create then remove the file structure.
    category_repo.save(sample_category)
    category_repo.delete('meeting-notes')

    # List should return an empty list.
    result = category_repo.list()
    assert result == []


# ** test_int: save_update
def test_int_save_update(category_repo: CategoryH5Repository, sample_category: CategoryAggregate):
    '''
    Test that saving an existing category updates its attributes.
    '''

    # Save the original category.
    category_repo.save(sample_category)

    # Mutate and re-save.
    sample_category.rename('Team Meeting Notes')
    category_repo.save(sample_category)

    # Retrieve and verify the update.
    result = category_repo.get('meeting-notes')
    assert result.name == 'Team Meeting Notes'


# ** test_int: delete_success
def test_int_delete_success(category_repo: CategoryH5Repository, sample_category: CategoryAggregate):
    '''
    Test that deleting a category removes it.
    '''

    # Save and delete the category.
    category_repo.save(sample_category)
    category_repo.delete('meeting-notes')

    # Assert the category no longer exists.
    assert category_repo.exists('meeting-notes') is False


# ** test_int: delete_idempotent
def test_int_delete_idempotent(category_repo: CategoryH5Repository, sample_category: CategoryAggregate):
    '''
    Test that deleting a non-existent category is idempotent.
    '''

    # Save a category to create the file.
    category_repo.save(sample_category)

    # Deleting a non-existent category should not raise.
    category_repo.delete('nonexistent')
