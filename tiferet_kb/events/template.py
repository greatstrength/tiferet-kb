"""tiferet_kb Template Events"""

# *** imports

# ** core
from typing import Any, List

# ** app
from tiferet.events import DomainEvent

from ..assets import constants as const
from ..domain.template import Template
from ..domain.document import Document
from ..interfaces.template import TemplateService
from ..interfaces.document import DocumentService
from ..mappers.template import TemplateAggregate, TemplateSectionAggregate
from ..mappers.document import DocumentAggregate, DocumentSectionAggregate

# *** events

# ** event: add_template
class AddTemplate(DomainEvent):
    '''
    Event to create a new knowledge base template.
    '''

    # * attribute: template_service
    template_service: TemplateService

    # * init
    def __init__(self, template_service: TemplateService):
        '''
        Initialize the AddTemplate event.

        :param template_service: The template service for persistence.
        :type template_service: TemplateService
        '''

        # Set the template service dependency.
        self.template_service = template_service

    # * method: execute
    @DomainEvent.parameters_required(['name'])
    def execute(self,
            name: str,
            id: str | None = None,
            description: str | None = None,
            category_id: str | None = None,
            sections: list | None = None,
            **kwargs,
        ) -> Template:
        '''
        Create a new template, optionally with initial sections.

        :param name: The template name.
        :type name: str
        :param id: Optional explicit UUID.
        :type id: str | None
        :param description: Optional description.
        :type description: str | None
        :param category_id: Optional suggested category.
        :type category_id: str | None
        :param sections: Optional list of section dicts with title, content_type, default_content.
        :type sections: list | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created template.
        :rtype: Template
        '''

        # Build the aggregate construction kwargs.
        tmpl_kwargs = dict(name=name)
        if id:
            tmpl_kwargs['id'] = id
        if description:
            tmpl_kwargs['description'] = description
        if category_id:
            tmpl_kwargs['category_id'] = category_id

        # Create the template aggregate.
        template = TemplateAggregate(**tmpl_kwargs)

        # Verify no duplicate.
        self.verify(
            expression=not self.template_service.exists(template.id),
            error_code=const.KB_TEMPLATE_ALREADY_EXISTS_ID,
            message=f'Template with ID {template.id} already exists.',
            id=template.id,
        )

        # Persist the template header.
        self.template_service.save(template)

        # Create and persist initial sections if provided.
        if sections:
            for position, sec_data in enumerate(sections):
                section = TemplateSectionAggregate(
                    template_id=template.id,
                    title=sec_data.get('title', ''),
                    content_type=sec_data.get('content_type', 'text'),
                    default_content=sec_data.get('default_content', ''),
                    position=position,
                )
                self.template_service.save_section(section)

        # Return the created template.
        return template


# ** event: get_template
class GetTemplate(DomainEvent):
    '''
    Event to retrieve a template by its identifier, including sections.
    '''

    # * attribute: template_service
    template_service: TemplateService

    # * init
    def __init__(self, template_service: TemplateService):
        '''
        Initialize the GetTemplate event.

        :param template_service: The template service for retrieval.
        :type template_service: TemplateService
        '''

        # Set the template service dependency.
        self.template_service = template_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> Template:
        '''
        Retrieve a template by ID.

        :param id: The template identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The retrieved template with sections.
        :rtype: Template
        '''

        # Retrieve the template.
        template = self.template_service.get(id)

        # Verify existence.
        self.verify(
            expression=template is not None,
            error_code=const.KB_TEMPLATE_NOT_FOUND_ID,
            template_id=id,
        )

        # Return the template.
        return template


# ** event: list_templates
class ListTemplates(DomainEvent):
    '''
    Event to list templates, optionally filtered by category.
    '''

    # * attribute: template_service
    template_service: TemplateService

    # * init
    def __init__(self, template_service: TemplateService):
        '''
        Initialize the ListTemplates event.

        :param template_service: The template service for listing.
        :type template_service: TemplateService
        '''

        # Set the template service dependency.
        self.template_service = template_service

    # * method: execute
    def execute(self, category_id: str | None = None, **kwargs) -> List[Template]:
        '''
        List templates.

        :param category_id: Optional category filter.
        :type category_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A list of templates.
        :rtype: List[Template]
        '''

        # Delegate to the template service.
        return self.template_service.list(category_id=category_id)


# ** event: update_template
class UpdateTemplate(DomainEvent):
    '''
    Event to update an existing template's metadata.

    Supports updating ``name``, ``description``, and ``category_id``.
    '''

    # * attribute: template_service
    template_service: TemplateService

    # * init
    def __init__(self, template_service: TemplateService):
        '''
        Initialize the UpdateTemplate event.

        :param template_service: The template service for retrieval and persistence.
        :type template_service: TemplateService
        '''

        # Set the template service dependency.
        self.template_service = template_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'attribute'])
    def execute(self,
            id: str,
            attribute: str,
            value: Any = None,
            **kwargs,
        ) -> Template:
        '''
        Update a template attribute.

        :param id: The template identifier.
        :type id: str
        :param attribute: The attribute to update (name, description, category_id).
        :type attribute: str
        :param value: The new value.
        :type value: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The updated template.
        :rtype: Template
        '''

        # Validate the attribute.
        valid_attributes = {'name', 'description', 'category_id'}
        self.verify(
            expression=attribute in valid_attributes,
            error_code=const.KB_TEMPLATE_NOT_FOUND_ID,
            message=f'Invalid template attribute: {attribute}',
            attribute=attribute,
        )

        # Retrieve the template.
        template = self.template_service.get(id)
        self.verify(
            expression=template is not None,
            error_code=const.KB_TEMPLATE_NOT_FOUND_ID,
            template_id=id,
        )

        # Apply the mutation.
        if attribute == 'name':
            template.rename(value)
        elif attribute == 'description':
            template.set_description(value)
        elif attribute == 'category_id':
            template.set_category(value)

        # Persist and return.
        self.template_service.save(template)
        return template


# ** event: remove_template
class RemoveTemplate(DomainEvent):
    '''
    Event to remove a template by ID (idempotent, cascading sections).
    '''

    # * attribute: template_service
    template_service: TemplateService

    # * init
    def __init__(self, template_service: TemplateService):
        '''
        Initialize the RemoveTemplate event.

        :param template_service: The template service for deletion.
        :type template_service: TemplateService
        '''

        # Set the template service dependency.
        self.template_service = template_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a template by ID.

        :param id: The template identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The removed template ID.
        :rtype: str
        '''

        # Delete the template (cascades to sections, idempotent).
        self.template_service.delete(id)
        return id


# ** event: apply_template
class ApplyTemplate(DomainEvent):
    '''
    Event to create a new document from a template.

    Stamps the template's section blueprints into new document sections,
    breaking the link — the document is independent after creation.
    '''

    # * attribute: template_service
    template_service: TemplateService

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, template_service: TemplateService, document_service: DocumentService):
        '''
        Initialize the ApplyTemplate event.

        :param template_service: The template service for retrieval.
        :type template_service: TemplateService
        :param document_service: The document service for persistence.
        :type document_service: DocumentService
        '''

        # Set dependencies.
        self.template_service = template_service
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['template_id', 'title'])
    def execute(self,
            template_id: str,
            title: str,
            folder_id: str | None = None,
            **kwargs,
        ) -> Document:
        '''
        Create a new document from a template.

        :param template_id: The template to apply.
        :type template_id: str
        :param title: The title for the new document.
        :type title: str
        :param folder_id: Optional folder to place the document in.
        :type folder_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created document.
        :rtype: Document
        '''

        # Retrieve the template with sections.
        template = self.template_service.get(template_id)
        self.verify(
            expression=template is not None,
            error_code=const.KB_TEMPLATE_NOT_FOUND_ID,
            template_id=template_id,
        )

        # Build the document kwargs.
        doc_kwargs = dict(
            title=title,
            template_id=template_id,
        )
        if template.category_id:
            doc_kwargs['category_id'] = template.category_id
        if folder_id:
            doc_kwargs['folder_id'] = folder_id

        # Create the document aggregate.
        document = DocumentAggregate(**doc_kwargs)

        # Persist the document header.
        self.document_service.save(document)

        # Stamp template sections into document sections.
        for tmpl_section in template.sections:
            doc_section = DocumentSectionAggregate(
                document_id=document.id,
                title=tmpl_section.title,
                content_type=tmpl_section.content_type,
                content=tmpl_section.default_content,
                position=tmpl_section.position,
            )
            self.document_service.save_section(doc_section)

        # Return the created document.
        return document
