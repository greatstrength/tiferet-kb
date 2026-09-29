"""tiferet_kb Template H5 Repository"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from tiferet_h5.repos import TableRepository

from ..interfaces.template import TemplateService
from ..mappers.template import (
    TemplateAggregate,
    TemplateSectionAggregate,
    TemplateTableObject,
    TemplateSectionTableObject,
)
from .core import KBH5Repository

# *** constants

# ** constant: templates_group
TEMPLATES_GROUP = '/kb/templates'

# ** constant: templates_table
TEMPLATES_TABLE = '/kb/templates/templates'

# ** constant: sections_table
TEMPLATE_SECTIONS_TABLE = '/kb/templates/template_sections'

# *** repos

# ** repo: template_table_repository
class TemplateTableRepository(TableRepository, KBH5Repository):
    '''
    Table collaborator for the template header rows.

    Owns ``/kb/templates/templates`` through ``TableRepository``.  It is not a
    service: ``TemplateH5Repository`` composes it, and both share one file.
    '''

    # * attribute: table_cls
    table_cls = TemplateTableObject

    # * attribute: table_path
    table_path = TEMPLATES_TABLE

# ** repo: template_section_table_repository
class TemplateSectionTableRepository(TableRepository, KBH5Repository):
    '''
    Table collaborator for the template section rows.

    Owns ``/kb/templates/template_sections`` through ``TableRepository``.  It
    is not a service: ``TemplateH5Repository`` composes it, and both share
    one file.
    '''

    # * attribute: table_cls
    table_cls = TemplateSectionTableObject

    # * attribute: table_path
    table_path = TEMPLATE_SECTIONS_TABLE

# ** repo: template_h5_repository
class TemplateH5Repository(KBH5Repository, TemplateService):
    '''
    HDF5-backed repository for knowledge base templates.

    Templates are stored as rows in ``/kb/templates/templates`` via
    ``TemplateTableObject``.  Template sections are stored as rows in
    ``/kb/templates/template_sections`` via ``TemplateSectionTableObject``.

    Each table is owned by a ``TableRepository`` collaborator; this class does
    not inherit the mixin, because ``get(id)`` and an append-only
    ``save(obj)`` would collide and one mixin has one ``table_path``.
    ``TableRepository.save`` only appends, so upsert here is delete-then-append.
    The first create of each table stamps ``schema_version``; ``verify`` is
    the opt-in check.
    '''

    # * attribute: templates_repo
    templates_repo: TemplateTableRepository

    # * attribute: sections_repo
    sections_repo: TemplateSectionTableRepository

    # * init
    def __init__(self, h5_file: str, mode: str = 'a') -> None:
        '''
        Initialize the template H5 repository and its table collaborators.

        :param h5_file: Path to the HDF5 file.
        :type h5_file: str
        :param mode: Default PyTables open mode.
        :type mode: str
        '''

        # Initialize the parent H5Repository.
        super().__init__(h5_file=h5_file, mode=mode)

        # Create one table collaborator per table, sharing the same file.
        self.templates_repo = TemplateTableRepository(h5_file=h5_file, mode=mode)
        self.sections_repo = TemplateSectionTableRepository(h5_file=h5_file, mode=mode)

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a template exists by ID.

        :param id: The template identifier.
        :type id: str
        :return: True if the template exists, otherwise False.
        :rtype: bool
        '''

        # Delegate to the header collaborator; a missing file or table is False.
        return self.templates_repo.exists(f'(id == b"{id}")')

    # * method: get
    def get(self, id: str) -> Optional[TemplateAggregate]:
        '''
        Retrieve a template by ID, including its sections.

        :param id: The template identifier.
        :type id: str
        :return: The template aggregate with sections, or None if not found.
        :rtype: TemplateAggregate | None
        '''

        # Read the header row through the collaborator.
        header = self.templates_repo.get(f'(id == b"{id}")')
        if header is None:
            return None

        # Map the template header.
        template = header.map()

        # Join the section rows, ordered by position.
        section_rows = self.sections_repo.list(f'(template_id == b"{id}")')
        template.sections = sorted(
            [row.map() for row in section_rows],
            key=lambda s: s.position,
        )

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

        # Build the optional category condition.
        condition = f'(category_id == b"{category_id}")' if category_id else None

        # Read header rows only; sections are not loaded.
        return [row.map() for row in self.templates_repo.list(condition)]

    # * method: save
    def save(self, template: TemplateAggregate) -> None:
        '''
        Save or update a template header (upsert).

        :param template: The template aggregate to save.
        :type template: TemplateAggregate
        :return: None
        :rtype: None
        '''

        # Convert the aggregate to a table object.
        table_obj = TemplateTableObject.from_model(template)

        # Upsert: remove the existing row when present, then append.
        condition = f'(id == b"{template.id}")'
        if self.templates_repo.exists(condition):
            self.templates_repo.delete(condition)
        self.templates_repo.save(table_obj)

    # * method: save_section
    def save_section(self, section: TemplateSectionAggregate) -> None:
        '''
        Save or update a template section (upsert).

        :param section: The template section aggregate to save.
        :type section: TemplateSectionAggregate
        :return: None
        :rtype: None
        '''

        # Convert the aggregate to a table object.
        table_obj = TemplateSectionTableObject.from_model(section)

        # Upsert: remove the existing row when present, then append.
        condition = f'(id == b"{section.id}")'
        if self.sections_repo.exists(condition):
            self.sections_repo.delete(condition)
        self.sections_repo.save(table_obj)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete a template and all its sections by ID (idempotent, cascading).

        :param id: The template identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # Remove the header row when present; a missing table is not an error.
        header_condition = f'(id == b"{id}")'
        if self.templates_repo.exists(header_condition):
            self.templates_repo.delete(header_condition)

        # Cascade to the section rows when present.
        section_condition = f'(template_id == b"{id}")'
        if self.sections_repo.exists(section_condition):
            self.sections_repo.delete(section_condition)

    # * method: verify
    def verify(self) -> None:
        '''
        Assert that each template table that exists matches its declared schema.

        This check is opt-in.  ``get``, ``list``, ``save``, and opening the
        file do not call it.  A missing file or table is not verified, and a
        table with no ``schema_version`` attribute is not a mismatch.  Column
        drift raises ``H5_SCHEMA_MISMATCH``.

        :return: None
        :rtype: None
        '''

        # A missing file has nothing to verify and must not be created.
        if not self.file_exists():
            return

        # Find which of the two tables exist.
        with self.client() as h5:
            present = [
                (collaborator, h5.node_exists(collaborator.table_path))
                for collaborator in (self.templates_repo, self.sections_repo)
            ]

        # Delegate to TableRepository.verify for each table that exists.
        for collaborator, exists in present:
            if exists:
                collaborator.verify()
