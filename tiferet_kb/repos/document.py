"""tiferet_kb Document H5 Repository"""

# *** imports

# ** core
from typing import Dict, List, Optional

# ** infra
import numpy as np

# ** app
from tiferet.assets import TiferetError
from tiferet_h5.repos import H5Repository

from ..interfaces.document import DocumentService
from ..domain.segment import TextSegment, Paragraph
from ..mappers.document import (
    DocumentAggregate,
    DocumentSectionAggregate,
    DocumentTableObject,
    DocumentSectionNodeObject,
)
from ..mappers.segment import HybridSegmentTableObject
from .core import KBNodeRepository, KBTableRepository

# *** constants

# ** constant: documents_group
DOCUMENTS_GROUP = '/kb/documents'

# ** constant: documents_table
DOCUMENTS_TABLE = '/kb/documents/documents'

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
    ``DocumentTableObject``.  Each section is a group node at
    ``/kb/documents/<document_id>/sections/<section_id>`` whose attributes
    come from ``DocumentSectionNodeObject`` and which holds a nested
    ``segments`` table (``HybridSegmentTableObject``).  Embeddings are two
    parallel arrays, ``section_embeddings`` and ``section_embedding_ids``.
    The ``get()`` method joins the header row and section groups to return
    a fully-populated aggregate.

    This class stays on ``H5Repository`` and does not inherit
    ``TableRepository`` or ``NodeRepository``: the header is a table, the
    section is a node plus a nested table, and the vectors are arrays.
    Group and array removal goes through ``KBNodeRepository.remove_node``,
    and stamped table creation through ``KBTableRepository.ensure_table``;
    each is held as a collaborator.
    The header and each ``segments`` table are stamped with
    ``schema_version`` on first create; ``verify`` is the opt-in check.
    '''

    # * attribute: node_repo
    node_repo: KBNodeRepository

    # * attribute: table_repo
    table_repo: KBTableRepository

    # * init
    def __init__(self, h5_file: str, mode: str = 'a') -> None:
        '''
        Initialize the document H5 repository and its node and table collaborators.

        :param h5_file: Path to the HDF5 file.
        :type h5_file: str
        :param mode: Default PyTables open mode.
        :type mode: str
        '''

        # Initialize the parent H5Repository.
        super().__init__(h5_file=h5_file, mode=mode)

        # Hold one collaborator per storage shape, sharing the same file.
        self.node_repo = KBNodeRepository(h5_file=h5_file, mode=mode)
        self.table_repo = KBTableRepository(h5_file=h5_file, mode=mode)

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

            # Load sections from group nodes.
            doc.sections = self._read_sections(h5, id)

        # Return the assembled document.
        return doc

    # * method: list
    def list(self,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
            status: Optional[str] = None,
            include_sections: bool = False,
        ) -> List[DocumentAggregate]:
        '''
        List documents with optional filters.

        :param folder_id: Optional folder identifier to filter by.
        :type folder_id: str | None
        :param category_id: Optional category identifier to filter by.
        :type category_id: str | None
        :param status: Optional status to filter by.
        :type status: str | None
        :param include_sections: If True, populate sections for each document.
        :type include_sections: bool
        :return: A list of document aggregates.
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

            # Map each row to an aggregate.
            docs = [DocumentTableObject.from_row(r).map() for r in rows]

            # Optionally load sections for each document.
            if include_sections:
                for doc in docs:
                    doc.sections = self._read_sections(h5, doc.id)

        # Return the document list.
        return docs

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

            # Get or create the documents table, stamping the schema on create.
            t = self.table_repo.ensure_table(
                h5,
                DOCUMENTS_TABLE,
                DocumentTableObject,
                title='Documents',
            )

            # Remove existing row if present (upsert).
            if h5.read_rows(DOCUMENTS_TABLE, condition=f'(id == b"{document.id}")'):
                h5.remove_rows(DOCUMENTS_TABLE, f'(id == b"{document.id}")')

            # Append the new row.
            table_obj.to_row(t)
            t.flush()

    # * method: verify
    def verify(self, section_path: Optional[str] = None) -> None:
        '''
        Assert that the live header table, and optionally one section's
        segments table, match their declared schemas.

        This check is opt-in.  ``get``, ``list``, ``save``, and opening the
        file do not call it.  A missing file or table is not verified, and a
        table with no ``schema_version`` attribute is not a mismatch.  Column
        drift raises ``H5_SCHEMA_MISMATCH``.

        :param section_path: Optional section group path,
            ``/kb/documents/<document_id>/sections/<section_id>``, whose
            ``segments`` table is verified as well.
        :type section_path: str | None
        :return: None
        :rtype: None
        '''

        # A missing file has nothing to verify and must not be created.
        if not self.file_exists():
            return

        with self.client() as h5:

            # Verify the header table when it exists.
            if h5.node_exists(DOCUMENTS_TABLE):
                h5.assert_schema(DOCUMENTS_TABLE, DocumentTableObject)

            # Verify the section's segments table when a path was given and it exists.
            if section_path:
                segments_path = f'{section_path}/segments'
                if h5.node_exists(segments_path):
                    h5.assert_schema(segments_path, HybridSegmentTableObject)

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
            sections_group = f'{DOCUMENTS_GROUP}/{id}/sections'
            section_ids = []
            if h5.node_exists(sections_group):
                root = h5.get_group(sections_group)
                section_ids = list(root._v_children.keys())

            # Remove the document row if the table exists.
            if h5.node_exists(DOCUMENTS_TABLE):
                h5.remove_rows(DOCUMENTS_TABLE, f'(id == b"{id}")')

            # Cascade: remove all section groups for this document.
            self.node_repo.remove_node(h5, f'{DOCUMENTS_GROUP}/{id}', recursive=True)

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
            return self._read_sections(h5, document_id)

    # * method: save_section
    def save_section(self, section: DocumentSectionAggregate) -> None:
        '''
        Save or update a document section (upsert).

        Creates a section group node with metadata attributes and a flat
        segments table containing denormalized paragraph data.  When the
        group already exists it is kept: attributes are written onto it and
        only the ``segments`` table is replaced, so any other child of the
        section group survives a passage rewrite.

        :param section: The document section aggregate to save.
        :type section: DocumentSectionAggregate
        :return: None
        :rtype: None
        '''

        with self.client() as h5:

            # Ensure parent groups exist.
            self._ensure_group(h5)
            doc_group = f'{DOCUMENTS_GROUP}/{section.document_id}'
            sections_group = f'{doc_group}/sections'
            self._ensure_path(h5, sections_group)
            section_group = f'{sections_group}/{section.id}'

            # Create the section group only when it is absent (upsert keeps it).
            if not h5.node_exists(section_group):
                h5.create_group(section_group, title=section.title)

            # Write section attributes onto the group.
            node_obj = DocumentSectionNodeObject.from_model(section)
            for attr_name, attr_value in node_obj.to_attrs().items():
                h5.set_node_attr(section_group, attr_name, attr_value)

            # Replace the segments table only, never the section group.
            segments_path = f'{section_group}/segments'
            self.node_repo.remove_node(h5, segments_path)
            t = self.table_repo.ensure_table(
                h5,
                segments_path,
                HybridSegmentTableObject,
                title='Segments',
            )

            # Write all segments with denormalized paragraph metadata.
            for paragraph in section.paragraphs:
                for segment in paragraph.segments:
                    obj = HybridSegmentTableObject(
                        paragraph_id=paragraph.id,
                        paragraph_position=paragraph.position,
                        block_type=paragraph.block_type,
                        id=segment.id,
                        position=segment.position,
                        text=segment.text,
                        format_type=segment.format_type,
                        link_url=segment.link_url or '',
                    )
                    obj.to_row(t)

            t.flush()

    # * method: delete_section
    def delete_section(self, section_id: str, document_id: str = None) -> None:
        '''
        Delete a document section by ID (idempotent).
        Also removes any embedding associated with the section.

        :param section_id: The section identifier.
        :type section_id: str
        :param document_id: The parent document identifier (needed to locate the section group).
        :type document_id: str
        :return: None
        :rtype: None
        '''

        with self.client() as h5:

            # Find and remove the section group.
            if document_id:
                section_group = f'{DOCUMENTS_GROUP}/{document_id}/sections/{section_id}'
                self.node_repo.remove_node(h5, section_group, recursive=True)
            else:
                # Search all document groups for the section.
                self._find_and_remove_section(h5, section_id)

            # Cascade: remove the section's embedding.
            self._remove_embedding_by_section_id(h5, section_id)

    # * method: reorder_sections
    def reorder_sections(self, document_id: str, section_ids: List[str]) -> None:
        '''
        Reorder sections within a document by updating position attributes.

        :param document_id: The parent document identifier.
        :type document_id: str
        :param section_ids: The section IDs in the desired order.
        :type section_ids: List[str]
        :return: None
        :rtype: None
        '''

        with self.client() as h5:

            sections_group = f'{DOCUMENTS_GROUP}/{document_id}/sections'

            # Return if the sections group does not exist.
            if not h5.node_exists(sections_group):
                return

            # Update position attribute on each section group.
            for position, section_id in enumerate(section_ids):
                section_path = f'{sections_group}/{section_id}'
                if h5.node_exists(section_path):
                    h5.set_node_attr(section_path, 'position', position)

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
                    TiferetError.raise_error(
                        const.KB_EMBEDDING_DIMENSION_MISMATCH_ID,
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
                self.node_repo.remove_node(h5, EMBEDDINGS_ARRAY)
                self.node_repo.remove_node(h5, EMBEDDING_IDS_ARRAY)

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
        self.node_repo.remove_node(h5, EMBEDDINGS_ARRAY)
        self.node_repo.remove_node(h5, EMBEDDING_IDS_ARRAY)

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
        self.node_repo.remove_node(h5, EMBEDDINGS_ARRAY)
        self.node_repo.remove_node(h5, EMBEDDING_IDS_ARRAY)

        # Recreate only if there are remaining embeddings.
        if mask.any():
            h5.create_array(EMBEDDINGS_ARRAY, embeddings[mask], title='Section Embeddings')
            h5.create_array(EMBEDDING_IDS_ARRAY, ids_raw[mask], title='Section Embedding IDs')

    # * method: _ensure_path
    def _ensure_path(self, h5, path: str) -> None:
        '''
        Create an HDF5 group at path if it does not exist, creating parents level-by-level.

        :param h5: The open H5Client instance.
        :param path: The target HDF5 group path.
        :type path: str
        :return: None
        :rtype: None
        '''

        if h5.node_exists(path):
            return

        # Split the path into segments and create each level.
        parts = [p for p in path.split('/') if p]
        for i in range(len(parts)):
            partial = '/' + '/'.join(parts[:i + 1])
            if not h5.node_exists(partial):
                h5.create_group(partial, title='')

    # * method: _read_sections
    def _read_sections(self, h5, document_id: str) -> List[DocumentSectionAggregate]:
        '''
        Read all sections for a document from group nodes, fully populating paragraphs.

        Called within an already-open ``h5`` context.

        :param h5: The open H5Client instance.
        :param document_id: The parent document identifier.
        :type document_id: str
        :return: A list of document section aggregates.
        :rtype: List[DocumentSectionAggregate]
        '''

        sections_group = f'{DOCUMENTS_GROUP}/{document_id}/sections'

        if not h5.node_exists(sections_group):
            return []

        sections_root = h5.get_group(sections_group)
        sections: List[DocumentSectionAggregate] = []

        for child in sections_root._v_children.values():
            section_id = child._v_name
            section_path = child._v_pathname

            # Read section attributes.
            section_attrs = h5.get_node_attrs(section_path)
            section_obj = DocumentSectionNodeObject.from_attrs(
                section_attrs, id=section_id, document_id=document_id,
            )

            # Read segments table and reconstruct paragraphs.
            segments_path = f'{section_path}/segments'
            paragraphs: List[Paragraph] = []

            if h5.node_exists(segments_path):
                rows = h5.read_rows(segments_path)

                # Group rows by paragraph_id.
                para_map: Dict[str, dict] = {}
                for row in rows:
                    pid = row['paragraph_id']
                    if pid not in para_map:
                        para_map[pid] = {
                            'id': pid,
                            'section_id': section_id,
                            'position': row['paragraph_position'],
                            'block_type': row['block_type'],
                            'segments': [],
                        }
                    link_url = row.get('link_url', '')
                    para_map[pid]['segments'].append(TextSegment(
                        id=row['id'],
                        position=row['position'],
                        text=row['text'],
                        format_type=row['format_type'],
                        link_url=link_url if link_url else None,
                    ))

                # Sort segments within each paragraph.
                for pdata in para_map.values():
                    pdata['segments'].sort(key=lambda s: s.position)
                    paragraphs.append(Paragraph(**pdata))

                paragraphs.sort(key=lambda p: p.position)

            section = section_obj.map(paragraphs=paragraphs)
            sections.append(section)

        sections.sort(key=lambda s: s.position)
        return sections

    # * method: _find_and_remove_section
    def _find_and_remove_section(self, h5, section_id: str) -> None:
        '''
        Search all document groups for a section and remove it.

        :param h5: The open H5Client instance.
        :param section_id: The section identifier to find and remove.
        :type section_id: str
        :return: None
        :rtype: None
        '''

        if not h5.node_exists(DOCUMENTS_GROUP):
            return

        docs_root = h5.get_group(DOCUMENTS_GROUP)
        for doc_child in docs_root._v_children.values():
            section_path = f'{doc_child._v_pathname}/sections/{section_id}'
            if h5.node_exists(section_path):
                self.node_repo.remove_node(h5, section_path, recursive=True)
                return

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

        # Get section IDs from group nodes for those documents.
        section_ids = set()
        for doc_id in doc_ids:
            sections_group = f'{DOCUMENTS_GROUP}/{doc_id}/sections'
            if h5.node_exists(sections_group):
                root = h5.get_group(sections_group)
                section_ids.update(root._v_children.keys())

        return section_ids
