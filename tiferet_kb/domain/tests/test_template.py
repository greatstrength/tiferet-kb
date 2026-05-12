"""tiferet_kb Template Domain Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..template import Template, TemplateSection

# *** tests

# ** test: template_auto_generates_defaults
def test_template_auto_generates_defaults():
    '''Test that Template auto-generates id and timestamps.'''

    tmpl = Template(name='Meeting Notes')
    assert tmpl.id is not None and len(tmpl.id) == 36
    assert tmpl.created_at is not None
    assert tmpl.updated_at is not None
    assert tmpl.sections == []


# ** test: template_preserves_explicit_id
def test_template_preserves_explicit_id():
    '''Test that an explicit id is preserved.'''

    tmpl = Template(id='tmpl-001', name='Test')
    assert tmpl.id == 'tmpl-001'


# ** test: template_optional_fields
def test_template_optional_fields():
    '''Test that optional fields default to None.'''

    tmpl = Template(name='Test')
    assert tmpl.description is None
    assert tmpl.category_id is None


# ** test: template_get_section
def test_template_get_section():
    '''Test get_section returns the correct section.'''

    sec = TemplateSection(template_id='t1', title='Intro', content_type='text', position=0)
    tmpl = Template(name='Test', sections=[sec])
    assert tmpl.get_section(0).title == 'Intro'
    assert tmpl.get_section(1) is None


# ** test: template_section_auto_generates_id
def test_template_section_auto_generates_id():
    '''Test that TemplateSection auto-generates id.'''

    sec = TemplateSection(template_id='t1', title='Intro', content_type='text', position=0)
    assert sec.id is not None and len(sec.id) == 36
    assert sec.default_content == ''


# ** test: template_rejects_extra_fields
def test_template_rejects_extra_fields():
    '''Test that extra fields are rejected.'''

    with pytest.raises(Exception):
        Template(name='Test', unknown_field='bad')
