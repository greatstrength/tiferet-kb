"""tiferet_kb Document H5 Repository"""

# *** imports

# ** core
from typing import Dict, List, Optional

# ** infra
import numpy as np

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

# ** constant: embeddings_array
EMBEDDINGS_ARRAY = '/kb/documents/section_embeddings'

# ** constant: embedding_ids_array
EMBEDDING_IDS_ARRAY = '/kb/documents/section_embedding_ids'

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
        Also removes any embeddings associated with the document's sections.

        :param id: The document identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        with self.client() as h5:

            # Collect section IDs before deleting, for embedding cleanup.
            section_ids = []
            if h5.node_exists(SECTIONS_TABLE):
                section_rows = h5.read_rows(
                    SECTIONS_TABLE,
                    condition=f'(document_id == b"{id}")',
                )
                section_ids = [r['id'] for r in section_rows]

            # Remove the document row if the table exists.
            if h5.node_exists(DOCUMENTS_TABLE):
                h5.remove_rows(DOCUMENTS_TABLE, f'(id == b"{id}")')

            # Cascade: remove all section rows for this document.
            if h5.node_exists(SECTIONS_TABLE):
                h5.remove_rows(SECTIONS_TABLE, f'(document_id == b"{id}")')

            # Cascade: remove embeddings for all deleted sections.
            if section_ids:
                self._remove_embeddings_by_section_ids(h5, section_ids)

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
        Also removes any embedding associated with the section.

        :param section_id: The section identifier.
        :type section_id: str
        :return: None
        :rtype: None
        '''

        with self.client() as h5:

            # Remove the section row if the table exists.
            if h5.node_exists(SECTIONS_TABLE):
                h5.remove_rows(SECTIONS_TABLE, f'(id == b"{section_id}")')

            # Cascade: remove the section's embedding.
            self._remove_embedding_by_section_id(h5, section_id)

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

    # * method: embed_section
    def embed_section(self,
            section_id: str,
            embedding: List[float],
            model_name: str,
        ) -> None:
        '''
        Store or replace an embedding vector for a document section.

        Uses two parallel HDF5 arrays: ``section_embeddings`` (float32 matrix)
        and ``section_embedding_ids`` (string index).  If the section already
        has an embedding, its row is replaced; otherwise a new row is appended.
        Raises a dimension mismatch error if the new vector's length differs
        from existing embeddings.

        :param section_id: The section identifier.
        :type section_id: str
        :param embedding: The embedding vector as a list of floats.
        :type embedding: List[float]
        :param model_name: The name of the embedding model.
        :type model_name: str
        :return: None
        :rtype: None
        '''

        # Convert the input vector to a float32 numpy array.
        new_vec = np.array(embedding, dtype=np.float32)

        with self.client() as h5:

            # Ensure the parent group exists.
            self._ensure_group(h5)

            # Load existing arrays if present.
            if h5.node_exists(EMBEDDINGS_ARRAY) and h5.node_exists(EMBEDDING_IDS_ARRAY):
                existing_embs = h5.get_array(EMBEDDINGS_ARRAY).read()
                existing_ids = h5.get_array(EMBEDDING_IDS_ARRAY).read()

                # Decode bytes to str for id comparison.
                id_list = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in existing_ids]

                # Validate dimension consistency.
                if existing_embs.shape[0] > 0 and existing_embs.shape[1] != new_vec.shape[0]:
                    from ..assets import constants as const
                    from tiferet.events import RaiseError
                    RaiseError.execute(
                        error_code=const.KB_EMBEDDING_DIMENSION_MISMATCH_ID,
                        expected=int(existing_embs.shape[1]),
                        actual=int(new_vec.shape[0]),
                    )

                # Replace or append.
                if section_id in id_list:
                    idx = id_list.index(section_id)
                    existing_embs[idx] = new_vec
                    new_embs = existing_embs
                    new_ids = existing_ids
                else:
                    new_embs = np.vstack([existing_embs, new_vec.reshape(1, -1)])
                    new_ids = np.append(existing_ids, np.bytes_(section_id))

                # Remove old arrays and recreate with updated data.
                h5.h5file.remove_node(EMBEDDINGS_ARRAY)
                h5.h5file.remove_node(EMBEDDING_IDS_ARRAY)

            else:
                # First embedding: create new arrays.
                new_embs = new_vec.reshape(1, -1)
                new_ids = np.array([section_id], dtype='S64')

            # Write the arrays.
            h5.create_array(EMBEDDINGS_ARRAY, new_embs, title='Section Embeddings')
            h5.create_array(EMBEDDING_IDS_ARRAY, new_ids, title='Section Embedding IDs')

    # * method: search_similar
    def search_similar(self,
            query_embedding: List[float],
            limit: int = 5,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
        ) -> List[Dict]:
        '''
        Brute-force cosine similarity search over stored embeddings.

        :param query_embedding: The query embedding vector.
        :type query_embedding: List[float]
        :param limit: Maximum number of results to return.
        :type limit: int
        :param folder_id: Optional folder identifier to filter by.
        :type folder_id: str | None
        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :return: A list of dicts with section_id and similarity score, ranked descending.
        :rtype: List[Dict]
        '''

        with self.client() as h5:

            # Return empty if embedding arrays do not exist.
            if not h5.node_exists(EMBEDDINGS_ARRAY) or not h5.node_exists(EMBEDDING_IDS_ARRAY):
                return []

            # Load embedding arrays.
            embeddings = h5.get_array(EMBEDDINGS_ARRAY).read()
            ids_raw = h5.get_array(EMBEDDING_IDS_ARRAY).read()

            # Return empty if no embeddings stored.
            if embeddings.shape[0] == 0:
                return []

            # Decode IDs.
            id_list = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in ids_raw]

            # Apply metadata filters if requested.
            if folder_id or category_id:
                allowed_section_ids = self._get_filtered_section_ids(h5, folder_id, category_id)
                mask = np.array([sid in allowed_section_ids for sid in id_list])
                if not mask.any():
                    return []
                embeddings = embeddings[mask]
                id_list = [sid for sid, m in zip(id_list, mask) if m]

            # Compute cosine similarity.
            query_vec = np.array(query_embedding, dtype=np.float32)
            query_norm = np.linalg.norm(query_vec)
            if query_norm == 0:
                return []
            query_vec = query_vec / query_norm

            emb_norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            # Guard against zero-norm embeddings.
            emb_norms = np.where(emb_norms == 0, 1, emb_norms)
            normed_embs = embeddings / emb_norms

            similarities = normed_embs @ query_vec

            # Get top-K indices.
            top_k = min(limit, len(similarities))
            top_indices = np.argsort(similarities)[::-1][:top_k]

        # Build result list.
        return [
            {'section_id': id_list[i], 'score': float(similarities[i])}
            for i in top_indices
        ]

    # * method: get_embedding
    def get_embedding(self, section_id: str) -> Optional[List[float]]:
        '''
        Retrieve the stored embedding for a section, or None if not embedded.

        :param section_id: The section identifier.
        :type section_id: str
        :return: The embedding vector, or None.
        :rtype: List[float] | None
        '''

        with self.client() as h5:

            # Return None if arrays do not exist.
            if not h5.node_exists(EMBEDDINGS_ARRAY) or not h5.node_exists(EMBEDDING_IDS_ARRAY):
                return None

            # Load arrays.
            embeddings = h5.get_array(EMBEDDINGS_ARRAY).read()
            ids_raw = h5.get_array(EMBEDDING_IDS_ARRAY).read()

            # Decode IDs and search.
            id_list = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in ids_raw]
            if section_id in id_list:
                idx = id_list.index(section_id)
                return embeddings[idx].tolist()

        # Not found.
        return None

    # * method: remove_embedding
    def remove_embedding(self, section_id: str) -> None:
        '''
        Remove the embedding for a section without deleting the section itself.

        :param section_id: The section identifier.
        :type section_id: str
        :return: None
        :rtype: None
        '''

        with self.client() as h5:

            # Delegate to the internal helper.
            self._remove_embedding_by_section_id(h5, section_id)

    # * method: _remove_embedding_by_section_id
    def _remove_embedding_by_section_id(self, h5, section_id: str) -> None:
        '''
        Remove a single section's embedding from the parallel arrays.

        Called within an already-open ``h5`` context.

        :param h5: The open H5Client instance.
        :param section_id: The section identifier to remove.
        :type section_id: str
        :return: None
        :rtype: None
        '''

        # Skip if arrays do not exist.
        if not h5.node_exists(EMBEDDINGS_ARRAY) or not h5.node_exists(EMBEDDING_IDS_ARRAY):
            return

        # Load arrays.
        embeddings = h5.get_array(EMBEDDINGS_ARRAY).read()
        ids_raw = h5.get_array(EMBEDDING_IDS_ARRAY).read()

        # Decode IDs.
        id_list = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in ids_raw]

        # Skip if section not found in index.
        if section_id not in id_list:
            return

        # Build mask excluding the target.
        mask = np.array([sid != section_id for sid in id_list])

        # Remove old arrays.
        h5.h5file.remove_node(EMBEDDINGS_ARRAY)
        h5.h5file.remove_node(EMBEDDING_IDS_ARRAY)

        # Recreate only if there are remaining embeddings.
        if mask.any():
            h5.create_array(EMBEDDINGS_ARRAY, embeddings[mask], title='Section Embeddings')
            h5.create_array(EMBEDDING_IDS_ARRAY, ids_raw[mask], title='Section Embedding IDs')

    # * method: _remove_embeddings_by_section_ids
    def _remove_embeddings_by_section_ids(self, h5, section_ids: List[str]) -> None:
        '''
        Remove embeddings for multiple sections from the parallel arrays.

        Called within an already-open ``h5`` context.

        :param h5: The open H5Client instance.
        :param section_ids: The section identifiers to remove.
        :type section_ids: List[str]
        :return: None
        :rtype: None
        '''

        # Skip if arrays do not exist.
        if not h5.node_exists(EMBEDDINGS_ARRAY) or not h5.node_exists(EMBEDDING_IDS_ARRAY):
            return

        # Load arrays.
        embeddings = h5.get_array(EMBEDDINGS_ARRAY).read()
        ids_raw = h5.get_array(EMBEDDING_IDS_ARRAY).read()

        # Decode IDs.
        id_list = [x.decode('utf-8') if isinstance(x, bytes) else str(x) for x in ids_raw]

        # Build mask excluding all target sections.
        remove_set = set(section_ids)
        mask = np.array([sid not in remove_set for sid in id_list])

        # Skip if nothing to remove.
        if mask.all():
            return

        # Remove old arrays.
        h5.h5file.remove_node(EMBEDDINGS_ARRAY)
        h5.h5file.remove_node(EMBEDDING_IDS_ARRAY)

        # Recreate only if there are remaining embeddings.
        if mask.any():
            h5.create_array(EMBEDDINGS_ARRAY, embeddings[mask], title='Section Embeddings')
            h5.create_array(EMBEDDING_IDS_ARRAY, ids_raw[mask], title='Section Embedding IDs')

    # * method: _get_filtered_section_ids
    def _get_filtered_section_ids(self,
            h5,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
        ) -> set:
        '''
        Get the set of section IDs belonging to documents matching the folder/category filters.

        :param h5: The open H5Client instance.
        :param folder_id: Optional folder identifier to filter by.
        :type folder_id: str | None
        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :return: Set of section IDs.
        :rtype: set
        '''

        # Build document filter condition.
        conditions = []
        if folder_id:
            conditions.append(f'(folder_id == b"{folder_id}")')
        if category_id:
            conditions.append(f'(category_id == b"{category_id}")')

        condition = ' & '.join(conditions) if conditions else None

        # Get matching document IDs.
        if not h5.node_exists(DOCUMENTS_TABLE):
            return set()
        doc_rows = h5.read_rows(DOCUMENTS_TABLE, condition=condition)
        doc_ids = {r['id'] for r in doc_rows}

        # Get section IDs for those documents.
        if not doc_ids or not h5.node_exists(SECTIONS_TABLE):
            return set()

        section_ids = set()
        for doc_id in doc_ids:
            section_rows = h5.read_rows(
                SECTIONS_TABLE,
                condition=f'(document_id == b"{doc_id}")',
            )
            section_ids.update(r['id'] for r in section_rows)

        return section_ids
