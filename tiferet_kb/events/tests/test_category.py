"""tiferet_kb Category Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events import DomainEvent
from tiferet.assets import TiferetError

from ...interfaces import CategoryService
from ...mappers import CategoryAggregate
from ..category import (
    AddCategory,
    GetCategory,
    ListCategories,
    UpdateCategory,
    RemoveCategory,
)

# *** fixtures

# ** fixture: mock_category_service
@pytest.fixture
def mock_category_service() -> CategoryService:
    '''
    Mock CategoryService for testing.
    '''
    return mock.Mock(spec=CategoryService)


# ** fixture: sample_category
@pytest.fixture
def sample_category() -> CategoryAggregate:
    '''
    Sample CategoryAggregate instance for testing.
    '''
    return CategoryAggregate(
        id='meeting-notes',
        name='Meeting Notes',
        description='Notes from meetings',
        icon='📝',
        color='#3B82F6',
    )

# *** tests

# ** test: add_category_success
def test_add_category_success(mock_category_service: CategoryService):
    '''
    Test successful creation of a new category.
    '''

    # Arrange the service to report no existing category.
    mock_category_service.exists.return_value = False

    # Execute via DomainEvent.handle.
    result = DomainEvent.handle(
        AddCategory,
        dependencies={'category_service': mock_category_service},
        id='meeting-notes',
        name='Meeting Notes',
        description='Notes from meetings',
    )

    # Assert the result is a Category with correct fields.
    assert result.id == 'meeting-notes'
    assert result.name == 'Meeting Notes'

    # Assert the service was called to save.
    mock_category_service.save.assert_called_once()


# ** test: add_category_duplicate
def test_add_category_duplicate(mock_category_service: CategoryService):
    '''
    Test that adding a duplicate category raises an error.
    '''

    # Arrange the service to report an existing category.
    mock_category_service.exists.return_value = True

    # Execute and expect a TiferetError.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddCategory,
            dependencies={'category_service': mock_category_service},
            id='meeting-notes',
            name='Meeting Notes',
        )


# ** test: add_category_missing_params
def test_add_category_missing_params(mock_category_service: CategoryService):
    '''
    Test that AddCategory raises an error when required params are missing.
    '''

    # Execute without required 'name' parameter.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            AddCategory,
            dependencies={'category_service': mock_category_service},
            id='meeting-notes',
        )


# ** test: get_category_success
def test_get_category_success(mock_category_service: CategoryService, sample_category: CategoryAggregate):
    '''
    Test successful retrieval of a category.
    '''

    # Arrange the service to return the sample category.
    mock_category_service.get.return_value = sample_category

    # Execute via DomainEvent.handle.
    result = DomainEvent.handle(
        GetCategory,
        dependencies={'category_service': mock_category_service},
        id='meeting-notes',
    )

    # Assert the result is the sample category.
    assert result is sample_category
    mock_category_service.get.assert_called_once_with('meeting-notes')


# ** test: get_category_not_found
def test_get_category_not_found(mock_category_service: CategoryService):
    '''
    Test that getting a non-existent category raises an error.
    '''

    # Arrange the service to return None.
    mock_category_service.get.return_value = None

    # Execute and expect a TiferetError.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            GetCategory,
            dependencies={'category_service': mock_category_service},
            id='nonexistent',
        )


# ** test: list_categories_success
def test_list_categories_success(mock_category_service: CategoryService, sample_category: CategoryAggregate):
    '''
    Test successful listing of categories.
    '''

    # Arrange the service to return a list.
    mock_category_service.list.return_value = [sample_category]

    # Execute via DomainEvent.handle.
    result = DomainEvent.handle(
        ListCategories,
        dependencies={'category_service': mock_category_service},
    )

    # Assert the result is a list with one category.
    assert len(result) == 1
    assert result[0] is sample_category


# ** test: update_category_success
def test_update_category_success(mock_category_service: CategoryService, sample_category: CategoryAggregate):
    '''
    Test successful update of a category attribute.
    '''

    # Arrange the service to return the sample category.
    mock_category_service.get.return_value = sample_category

    # Execute via DomainEvent.handle.
    result = DomainEvent.handle(
        UpdateCategory,
        dependencies={'category_service': mock_category_service},
        id='meeting-notes',
        attribute='name',
        value='Team Meeting Notes',
    )

    # Assert the name was updated.
    assert result.name == 'Team Meeting Notes'

    # Assert the service was called to save.
    mock_category_service.save.assert_called_once()


# ** test: update_category_invalid_attribute
def test_update_category_invalid_attribute(mock_category_service: CategoryService):
    '''
    Test that updating an invalid attribute raises an error.
    '''

    # Execute with an invalid attribute name.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            UpdateCategory,
            dependencies={'category_service': mock_category_service},
            id='meeting-notes',
            attribute='nonexistent',
            value='bad',
        )


# ** test: remove_category_success
def test_remove_category_success(mock_category_service: CategoryService):
    '''
    Test successful removal of a category.
    '''

    # Execute via DomainEvent.handle.
    result = DomainEvent.handle(
        RemoveCategory,
        dependencies={'category_service': mock_category_service},
        id='meeting-notes',
    )

    # Assert the returned ID matches.
    assert result == 'meeting-notes'

    # Assert the service delete was called.
    mock_category_service.delete.assert_called_once_with('meeting-notes')
