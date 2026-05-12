"""tiferet_kb Template Mappers"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List

# ** infra
import tables
from pydantic import Field

# ** app
from tiferet.mappers import Aggregate
from tiferet_h5.mappers import TableObject

from ..domain.template import Template, TemplateSection

# *** mappers

# ** mapper: template_section_aggregate
class TemplateSectionAggregate(TemplateSection, Aggregate):
    '''
    A mutable aggregate representation of a template section blueprint.
    '''

    # * method: rename
    def rename(self, title: str) -> None:
        '''
        Rename the template section.

        :param title: The new section title.
        :type title: str
        :return: None
        :rtype: None
        '''

        # Update the title.
        self.title = title

    # * method: set_default_content
    def set_default_content(self, default_content: str) -> None:
        '''
        Set the default content for the template section.

        :param default_content: The new default content.
        :type default_content: str
        :return: None
        :rtype: None
        '''

        # Update the default content.
        self.default_content = default_content

    # * method: set_content_type
    def set_content_type(self, content_type: str) -> None:
        '''
        Set the content type for the template section.

        :param content_type: The new content type.
        :type content_type: str
        :return: None
        :rtype: None
        '''

        # Update the content type.
        self.content_type = content_type


# ** mapper: template_aggregate
class TemplateAggregate(Template, Aggregate):
    '''
    A mutable aggregate representation of a knowledge base template.
    '''

    # * attribute: sections
    sections: List[TemplateSectionAggregate] = Field(
        default_factory=list,
        description='Ordered list of mutable template section aggregates.',
    )

    # * method: rename
    def rename(self, name: str) -> None:
        '''
        Rename the template.

        :param name: The new template name.
        :type name: str
        :return: None
        :rtype: None
        '''

        # Update the name and timestamp.
        self.name = name
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_description
    def set_description(self, description: str | None) -> None:
        '''
        Set the template description.

        :param description: The new description, or None to clear.
        :type description: str | None
        :return: None
        :rtype: None
        '''

        # Update the description and timestamp.
        self.description = description
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_category
    def set_category(self, category_id: str | None) -> None:
        '''
        Set the suggested category for documents created from this template.

        :param category_id: The category identifier, or None to clear.
        :type category_id: str | None
        :return: None
        :rtype: None
        '''

        # Update the category and timestamp.
        self.category_id = category_id
        self.updated_at = datetime.now(timezone.utc).isoformat()


# ** mapper: template_table_object
class TemplateTableObject(TableObject):
    '''
    An HDF5 table-row representation of a template header.

    Stored as rows in ``/kb/templates/templates``.
    '''

    # * attribute: id
    id: str = Field(default='', description='Template UUID.')

    # * attribute: name
    name: str = Field(default='', description='Template name.')

    # * attribute: description
    description: str = Field(default='', description='Template description.')

    # * attribute: category_id
    category_id: str = Field(default='', description='Suggested category identifier.')

    # * attribute: created_at
    created_at: str = Field(default='', description='ISO 8601 creation timestamp.')

    # * attribute: updated_at
    updated_at: str = Field(default='', description='ISO 8601 last-updated timestamp.')

    # * attribute: _H5_TYPES
    _H5_TYPES: ClassVar[Dict[str, Any]] = {
        'id':          tables.StringCol(64),
        'name':        tables.StringCol(512),
        'description': tables.StringCol(1024),
        'category_id': tables.StringCol(64),
        'created_at':  tables.StringCol(32),
        'updated_at':  tables.StringCol(32),
    }

    # * method: map
    def map(self, **overrides) -> TemplateAggregate:
        '''
        Map the table object data to a template aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new template aggregate (without sections).
        :rtype: TemplateAggregate
        '''

        # Serialize and construct the aggregate, converting empty strings to None.
        data = self.to_primitive()
        for field in ('description', 'category_id'):
            if data.get(field) == '':
                data[field] = None
        data.update(overrides)

        # Return the constructed aggregate.
        return TemplateAggregate(**data)

    # * method: from_model
    @classmethod
    def from_model(cls, template: Template, **overrides) -> 'TemplateTableObject':
        '''
        Create a TemplateTableObject from a Template model.

        :param template: The template model to copy from.
        :type template: Template
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new TemplateTableObject.
        :rtype: TemplateTableObject
        '''

        # Dump the model, excluding sections, and replace None with ''.
        data = template.model_dump(by_alias=False, exclude={'sections'})
        for field in ('description', 'category_id'):
            if data.get(field) is None:
                data[field] = ''
        data.update(overrides)

        # Construct and return the table object.
        return cls.model_validate(data)


# ** mapper: template_section_table_object
class TemplateSectionTableObject(TableObject):
    '''
    An HDF5 table-row representation of a template section blueprint.

    Stored as rows in ``/kb/templates/template_sections``.
    '''

    # * attribute: id
    id: str = Field(default='', description='Section UUID.')

    # * attribute: template_id
    template_id: str = Field(default='', description='Parent template UUID.')

    # * attribute: title
    title: str = Field(default='', description='Default section heading.')

    # * attribute: content_type
    content_type: str = Field(default='', description='Default content type.')

    # * attribute: default_content
    default_content: str = Field(default='', description='Pre-filled content.')

    # * attribute: position
    position: int = Field(default=0, description='Ordering position.')

    # * attribute: _H5_TYPES
    _H5_TYPES: ClassVar[Dict[str, Any]] = {
        'id':              tables.StringCol(64),
        'template_id':     tables.StringCol(64),
        'title':           tables.StringCol(512),
        'content_type':    tables.StringCol(32),
        'default_content': tables.StringCol(65536),
        'position':        tables.Int32Col(),
    }

    # * method: map
    def map(self, **overrides) -> TemplateSectionAggregate:
        '''
        Map the table object data to a template section aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new template section aggregate.
        :rtype: TemplateSectionAggregate
        '''

        # Serialize and construct the aggregate.
        data = self.to_primitive()
        data.update(overrides)
        return TemplateSectionAggregate(**data)

    # * method: from_model
    @classmethod
    def from_model(cls, section: TemplateSection, **overrides) -> 'TemplateSectionTableObject':
        '''
        Create a TemplateSectionTableObject from a TemplateSection model.

        :param section: The section model to copy from.
        :type section: TemplateSection
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new TemplateSectionTableObject.
        :rtype: TemplateSectionTableObject
        '''

        # Dump the model and construct the table object.
        data = section.model_dump(by_alias=False)
        data.update(overrides)
        return cls.model_validate(data)
