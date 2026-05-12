"""tiferet_kb Document H5 Repository"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from tiferet_h5.repos import H5Repository

from ..interfaces.document import DocumentService
from ..mappers.document import (
    DocumentAggregate,
    DocumentSectionAggregate,
    DocumentTableObject,
    DocumentSectionTableObject,
)

# *** constants

# ** constant: documents_group
DOCUMENTS_GROUP = '/kb/documents'

# ** constant: documents_table
DOCUMENTS_TABLE = '/kb/documents/documents'

# ** constant: sections_table
SECTIONS_TABLE = '/kb/documents/document_sections'

# *** repos

# ** repo: document_h5_repository
class DocumentH5Repository(H5Repository, DocumentService):
    '''
    HDF5-backed repository for knowledge base documents.

    Documents are stored as rows in ``/kb/documents/documents`` via
    ``DocumentTableObject``.  Sections are stored as rows in
    ``/kb/documents/document_sections`` via ``DocumentSectionTableObject``.
    The ``get()`` method joins header and section rows to return a
    fully-populated aggregate.
    '''

    # * init
    def __init__(self, h5_file: str, mode: str = 'a') -> None:
        '''
        Initialize the document H5 repository.

        :param h5_file: Path to the HDF5 file.
        :type h5_file: str
        :param mode: Default PyTables open mode.
        :type mode: str
        '''

        # Initialize the parent H5Repository.
        super().__init__(h5_file=h5_file, mode=mode)

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a document exists by ID.

        :param id: The document identifier.
        :type id: str
        :return: True if the document exists, otherwise False.
        :rtype: bool
        '''

        with self.client() as h5:

            # Return False if the table does not exist yet.
            if not h5.node_exists(DOCUMENTS_TABLE):
                return False

            # Query for the document id.
            rows = h5.read_rows(DOCUMENTS_TABLE, condition=f'(id == b"{id}")')
            return len(rows) > 0

    # * method: get
    def get(self, id: str) -> Optional[DocumentAggregate]:
        '''
        Retrieve a document by ID, including its sections.

        :param id: The document identifier.
        :type id: str
        :return: The document aggregate with sections, or None if not found.
        :rtype: DocumentAggregate | None
        '''

        with self.client() as h5:

            # Return None if the table does not exist.
            if not h5.node_exists(DOCUMENTS_TABLE):
                return None

            # Query for the document row.
            doc_rows = h5.read_rows(DOCUMENTS_TABLE, condition=f'(id == b"{id}")')
            if not doc_rows:
                return None

            # Map the document header.
            doc = DocumentTableObject.from_row(doc_rows[0]).map()

            # Load sections if the sections table exists.
            if h5.node_exists(SECTIONS_TABLE):
                section_rows = h5.read_rows(
                    SECTIONS_TABLE,
                    condition=f'(document_id == b"{id}")',
                )
                sections = sorted(
                    [DocumentSectionTableObject.from_row(r).map() for r in section_rows],
                    key=lambda s: s.position,
                )
                doc.sections = sections

        # Return the assembled document.
        return doc

    # * method: list
    def list(self,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
            status: Optional[str] = None,
        ) -> List[DocumentAggregate]:
        '''
        List documents with optional filters.

        :param folder_id: Optional folder identifier to filter by.
        :type folder_id: str | None
        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :param status: Optional status to filter by.
        :type status: str | None
        :return: A list of document aggregates (without sections).
        :rtype: List[DocumentAggregate]
        '''

        with self.client() as h5:

            # Return empty if the table does not exist.
            if not h5.node_exists(DOCUMENTS_TABLE):
                return []

            # Build the condition from filters.
            conditions = []
            if folder_id:
                conditions.append(f'(folder_id == b"{folder_id}")')
            if category_id:
                conditions.append(f'(category_id == b"{category_id}")')
            if status:
                conditions.append(f'(status == b"{status}")')

            # Read rows with or without condition.
            condition = ' & '.join(conditions) if conditions else None
            rows = h5.read_rows(DOCUMENTS_TABLE, condition=condition)

        # Map each row to an aggregate (without sections for list view).
        return [DocumentTableObject.from_row(r).map() for r in rows]

    # * method: save
    def save(self, document: DocumentAggregate) -> None:
        '''
        Save or update a document header (upsert).

        :param document: The document aggregate to save.
        :type document: DocumentAggregate
        :return: None
        :rtype: None
        '''

        # Convert to table object.
        table_obj = DocumentTableObject.from_model(document)

        with self.client() as h5:

            # Ensure the parent group exists.
            self._ensure_group(h5)

            # Get or create the documents table.
            t = h5.get_or_create_table(
                DOCUMENTS_TABLE,
                DocumentTableObject.get_description(),
                title='Documents',
            )

            # Remove existing row if present (upsert).
            if h5.read_rows(DOCUMENTS_TABLE, condition=f'(id == b"{document.id}")'):
                h5.remove_rows(DOCUMENTS_TABLE, f'(id == b"{document.id}")')

            # Append the new row.
            table_obj.to_row(t)
            t.flush()

    # * method: _ensure_group
    def _ensure_group(self, h5) -> None:
        '''
        Ensure the ``/kb/documents`` parent group exists.

        :param h5: The open H5Client instance.
        :return: None
        :rtype: None
        '''

        # Create /kb if absent.
        if not h5.node_exists('/kb'):
            h5.create_group('/kb', title='Knowledge Base')

        # Create /kb/documents if absent.
        if not h5.node_exists(DOCUMENTS_GROUP):
            h5.create_group(DOCUMENTS_GROUP, title='Documents')

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete a document and all its sections by ID (idempotent, cascading).

        :param id: The document identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        with self.client() as h5:

            # Remove the document row if the table exists.
            if h5.node_exists(DOCUMENTS_TABLE):
                h5.remove_rows(DOCUMENTS_TABLE, f'(id == b"{id}")')

            # Cascade: remove all section rows for this document.
            if h5.node_exists(SECTIONS_TABLE):
                h5.remove_rows(SECTIONS_TABLE, f'(document_id == b"{id}")')

    # * method: get_sections
    def get_sections(self, document_id: str) -> List[DocumentSectionAggregate]:
        '''
        Retrieve all sections for a document, ordered by position.

        :param document_id: The parent document identifier.
        :type document_id: str
        :return: A list of document section aggregates.
        :rtype: List[DocumentSectionAggregate]
        '''

        with self.client() as h5:

            # Return empty if the sections table does not exist.
            if not h5.node_exists(SECTIONS_TABLE):
                return []

            # Query sections by document_id.
            rows = h5.read_rows(
                SECTIONS_TABLE,
                condition=f'(document_id == b"{document_id}")',
            )

        # Map and sort by position.
        return sorted(
            [DocumentSectionTableObject.from_row(r).map() for r in rows],
            key=lambda s: s.position,
        )

    # * method: save_section
    def save_section(self, section: DocumentSectionAggregate) -> None:
        '''
        Save or update a document section (upsert).

        :param section: The document section aggregate to save.
        :type section: DocumentSectionAggregate
        :return: None
        :rtype: None
        '''

        # Convert to table object.
        table_obj = DocumentSectionTableObject.from_model(section)

        with self.client() as h5:

            # Ensure the parent group exists.
            self._ensure_group(h5)

            # Get or create the sections table.
            t = h5.get_or_create_table(
                SECTIONS_TABLE,
                DocumentSectionTableObject.get_description(),
                title='Document Sections',
            )

            # Remove existing row if present (upsert).
            if h5.read_rows(SECTIONS_TABLE, condition=f'(id == b"{section.id}")'):
                h5.remove_rows(SECTIONS_TABLE, f'(id == b"{section.id}")')

            # Append the new row.
            table_obj.to_row(t)
            t.flush()

    # * method: delete_section
    def delete_section(self, section_id: str) -> None:
        '''
        Delete a document section by ID (idempotent).

        :param section_id: The section identifier.
        :type section_id: str
        :return: None
        :rtype: None
        '''

        with self.client() as h5:

            # Remove the section row if the table exists.
            if h5.node_exists(SECTIONS_TABLE):
                h5.remove_rows(SECTIONS_TABLE, f'(id == b"{section_id}")')

    # * method: reorder_sections
    def reorder_sections(self, document_id: str, section_ids: List[str]) -> None:
        '''
        Reorder sections within a document.

        :param document_id: The parent document identifier.
        :type document_id: str
        :param section_ids: The section IDs in the desired order.
        :type section_ids: List[str]
        :return: None
        :rtype: None
        '''

        with self.client() as h5:

            # Return if the sections table does not exist.
            if not h5.node_exists(SECTIONS_TABLE):
                return

            # Load all sections for this document.
            rows = h5.read_rows(
                SECTIONS_TABLE,
                condition=f'(document_id == b"{document_id}")',
            )

            # Index sections by id.
            sections_by_id = {r['id']: r for r in rows}

            # Remove all existing section rows for this document.
            h5.remove_rows(SECTIONS_TABLE, f'(document_id == b"{document_id}")')

            # Re-append in the new order with updated positions.
            t = h5.get_table(SECTIONS_TABLE)
            for position, section_id in enumerate(section_ids):
                if section_id not in sections_by_id:
                    continue
                section_data = sections_by_id[section_id]
                section_data['position'] = position
                obj = DocumentSectionTableObject.from_row(section_data)
                obj.position = position
                obj.to_row(t)

            t.flush()
