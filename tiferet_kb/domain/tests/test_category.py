"""tiferet_kb Category Domain Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..category import Category

# *** tests

# ** test: category_construction
def test_category_construction():
    '''
    Test basic construction of a Category domain object with all fields.
    '''

    # Construct a category with all fields populated.
    category = Category(
        id='meeting-notes',
        name='Meeting Notes',
        description='Notes from meetings',
        icon='📝',
        color='#3B82F6',
    )

    # Assert all fields match.
    assert category.id == 'meeting-notes'
    assert category.name == 'Meeting Notes'
    assert category.description == 'Notes from meetings'
    assert category.icon == '📝'
    assert category.color == '#3B82F6'


# ** test: category_optional_fields_default_none
def test_category_optional_fields_default_none():
    '''
    Test that optional fields default to None.
    '''

    # Construct a category with only required fields.
    category = Category(id='design-docs', name='Design Docs')

    # Assert optional fields are None.
    assert category.description is None
    assert category.icon is None
    assert category.color is None


# ** test: category_rejects_extra_fields
def test_category_rejects_extra_fields():
    '''
    Test that DomainObject's extra='forbid' rejects unknown fields.
    '''

    # Attempt to construct with an unknown field.
    with pytest.raises(Exception):
        Category(id='test', name='Test', unknown_field='bad')
