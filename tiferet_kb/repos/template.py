"""tiferet_kb Template H5 Repository"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from tiferet_h5.repos import H5Repository

from ..interfaces.template import TemplateService
from ..mappers.template import (
    TemplateAggregate,
    TemplateSectionAggregate,
    TemplateTableObject,
    TemplateSectionTableObject,
)

# *** constants

# ** constant: templates_group
TEMPLATES_GROUP = '/kb/templates'

# ** constant: templates_table
TEMPLATES_TABLE = '/kb/templates/templates'

# ** constant: sections_table
TEMPLATE_SECTIONS_TABLE = '/kb/templates/template_sections'

# *** repos

# ** repo: template_h5_repository
class TemplateH5Repository(H5Repository, TemplateService):
    '''
    HDF5-backed repository for knowledge base templates.

    Templates are stored as rows in ``/kb/templates/templates`` via
    ``TemplateTableObject``.  Template sections are stored as rows in
    ``/kb/templates/template_sections`` via ``TemplateSectionTableObject``.
    '''

    # * init
    def __init__(self, h5_file: str, mode: str = 'a') -> None:
        '''
        Initialize the template H5 repository.

        :param h5_file: Path to the HDF5 file.
        :type h5_file: str
        :param mode: Default PyTables open mode.
        :type mode: str
        '''

        # Initialize the parent H5Repository.
        super().__init__(h5_file=h5_file, mode=mode)

    # * method: _ensure_group
    def _ensure_group(self, h5) -> None:
        '''
        Ensure the ``/kb/templates`` parent group exists.

        :param h5: The open H5Client instance.
        :return: None
        :rtype: None
        '''

        # Create /kb if absent.
        if not h5.node_exists('/kb'):
            h5.create_group('/kb', title='Knowledge Base')

        # Create /kb/templates if absent.
        if not h5.node_exists(TEMPLATES_GROUP):
            h5.create_group(TEMPLATES_GROUP, title='Templates')

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a template exists by ID.

        :param id: The template identifier.
        :type id: str
        :return: True if the template exists, otherwise False.
        :rtype: bool
        '''

        with self.client() as h5:
            if not h5.node_exists(TEMPLATES_TABLE):
                return False
            rows = h5.read_rows(TEMPLATES_TABLE, condition=f'(id == b"{id}")')
            return len(rows) > 0

    # * method: get
    def get(self, id: str) -> Optional[TemplateAggregate]:
        '''
        Retrieve a template by ID, including its sections.

        :param id: The template identifier.
        :type id: str
        :return: The template aggregate with sections, or None if not found.
        :rtype: TemplateAggregate | None
        '''

        with self.client() as h5:
            if not h5.node_exists(TEMPLATES_TABLE):
                return None

            rows = h5.read_rows(TEMPLATES_TABLE, condition=f'(id == b"{id}")')
            if not rows:
                return None

            # Map the template header.
            template = TemplateTableObject.from_row(rows[0]).map()

            # Load sections if the sections table exists.
            if h5.node_exists(TEMPLATE_SECTIONS_TABLE):
                section_rows = h5.read_rows(
                    TEMPLATE_SECTIONS_TABLE,
                    condition=f'(template_id == b"{id}")',
                )
                sections = sorted(
                    [TemplateSectionTableObject.from_row(r).map() for r in section_rows],
                    key=lambda s: s.position,
                )
                template.sections = sections

        # Return the assembled template.
        return template

    # * method: list
    def list(self, category_id: Optional[str] = None) -> List[TemplateAggregate]:
        '''
        List templates, optionally filtered by category.

        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :return: A list of template aggregates (without sections).
        :rtype: List[TemplateAggregate]
        '''

        with self.client() as h5:
            if not h5.node_exists(TEMPLATES_TABLE):
                return []

            condition = f'(category_id == b"{category_id}")' if category_id else None
            rows = h5.read_rows(TEMPLATES_TABLE, condition=condition)

        return [TemplateTableObject.from_row(r).map() for r in rows]

    # * method: save
    def save(self, template: TemplateAggregate) -> None:
        '''
        Save or update a template header (upsert).

        :param template: The template aggregate to save.
        :type template: TemplateAggregate
        :return: None
        :rtype: None
        '''

        table_obj = TemplateTableObject.from_model(template)

        with self.client() as h5:
            self._ensure_group(h5)

            t = h5.get_or_create_table(
                TEMPLATES_TABLE,
                TemplateTableObject.get_description(),
                title='Templates',
            )

            # Upsert: remove existing row then append.
            if h5.read_rows(TEMPLATES_TABLE, condition=f'(id == b"{template.id}")'):
                h5.remove_rows(TEMPLATES_TABLE, f'(id == b"{template.id}")')

            table_obj.to_row(t)
            t.flush()

    # * method: save_section
    def save_section(self, section: TemplateSectionAggregate) -> None:
        '''
        Save or update a template section (upsert).

        :param section: The template section aggregate to save.
        :type section: TemplateSectionAggregate
        :return: None
        :rtype: None
        '''

        table_obj = TemplateSectionTableObject.from_model(section)

        with self.client() as h5:
            self._ensure_group(h5)

            t = h5.get_or_create_table(
                TEMPLATE_SECTIONS_TABLE,
                TemplateSectionTableObject.get_description(),
                title='Template Sections',
            )

            # Upsert: remove existing row then append.
            if h5.read_rows(TEMPLATE_SECTIONS_TABLE, condition=f'(id == b"{section.id}")'):
                h5.remove_rows(TEMPLATE_SECTIONS_TABLE, f'(id == b"{section.id}")')

            table_obj.to_row(t)
            t.flush()

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete a template and all its sections by ID (idempotent, cascading).

        :param id: The template identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        with self.client() as h5:
            if h5.node_exists(TEMPLATES_TABLE):
                h5.remove_rows(TEMPLATES_TABLE, f'(id == b"{id}")')
            if h5.node_exists(TEMPLATE_SECTIONS_TABLE):
                h5.remove_rows(TEMPLATE_SECTIONS_TABLE, f'(template_id == b"{id}")')
