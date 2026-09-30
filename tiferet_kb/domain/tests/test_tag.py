"""tiferet_kb Tag Domain Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..document import Document, DocumentSection
from ..tag import Tag

# *** tests

# ** test: tag_construction
def test_tag_construction():
    '''
    Test basic construction of a Tag with all fields.
    '''

    # Construct a tag with all fields populated.
    tag = Tag(id='My-Tag', name='Release', color='blue')

    # Assert the id is stored as given and the other fields match.
    assert tag.id == 'My-Tag'
    assert tag.name == 'Release'
    assert tag.color == 'blue'

# ** test: tag_color_defaults_none
def test_tag_color_defaults_none():
    '''
    Test that color defaults to None when omitted.
    '''

    # Construct a tag with only required fields.
    tag = Tag(id='design', name='Design')

    # Assert color is absent.
    assert tag.color is None

# ** test: tag_fields_are_id_name_color
def test_tag_fields_are_id_name_color():
    '''
    A tag is not a second category: no description, icon, or parent.
    '''

    # Assert the declared fields.
    assert set(Tag.model_fields) == {'id', 'name', 'color'}

# ** test: tag_rejects_extra_fields
def test_tag_rejects_extra_fields():
    '''
    Test that DomainObject's extra='forbid' rejects a parent or description.
    '''

    # Attempt to construct with fields a category has and a tag does not.
    with pytest.raises(Exception):
        Tag(id='test', name='Test', description='nope')
    with pytest.raises(Exception):
        Tag(id='test', name='Test', parent='other')

# ** test: document_has_no_tags_or_content_field
def test_document_has_no_tags_or_content_field():
    '''
    Document and DocumentSection do not gain tags or a content column.
    '''

    # Assert the header and section models stay free of those fields.
    assert 'tags' not in Document.model_fields
    assert 'content' not in Document.model_fields
    assert 'tag_id' not in Document.model_fields
    assert 'tags' not in DocumentSection.model_fields
    assert 'content' not in DocumentSection.model_fields
