"""tiferet_kb Tag H5 Repository"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from tiferet_h5.repos import NodeRepository

from ..interfaces.tag import TagService
from ..mappers.tag import (
    DocumentTagTableObject,
    TagAggregate,
    TagNodeObject,
)
from .core import KBNodeRepository, KBTableRepository

# *** constants

# ** constant: tags_root
TAGS_ROOT = '/kb/tags'

# ** constant: document_tags_table
DOCUMENT_TAGS_TABLE = '/kb/document_tags'

# *** repos

# ** repo: document_tag_table_repository
class DocumentTagTableRepository(KBTableRepository):
    '''
    Table collaborator for document–tag association rows.

    Owns the association table through ``TableRepository``. It is not a
    service: ``TagH5Repository`` composes it, and both share one file.
    Row removal uses ``TableRepository.delete``, not a direct file-node removal.
    '''

    # * attribute: table_cls
    table_cls = DocumentTagTableObject

    # * attribute: table_path
    table_path = DOCUMENT_TAGS_TABLE

# ** repo: tag_h5_repository
class TagH5Repository(KBNodeRepository, TagService):
    '''
    HDF5-backed repository for tag labels and document–tag associations.

    Labels are group attributes, the same shape as categories. The
    association is a separate table so a document can carry many tags
    without a header column. The two mixins collide on ``save``, ``get``,
    and ``exists``, so the table is a collaborator rather than a second
    base class.

    Paths are an implementation layout on the aligned layer, not a
    published contract. Label removal goes through
    ``KBNodeRepository.remove_node``. Association removal goes through
    ``TableRepository.delete``.
    '''

    # * attribute: node_cls
    node_cls = TagNodeObject

    # * attribute: node_path
    node_path = f'{TAGS_ROOT}/{{id}}'

    # * attribute: associations
    associations: DocumentTagTableRepository

    # * init
    def __init__(self, h5_file: str, mode: str = 'a') -> None:
        '''
        Initialize the tag H5 repository and its association collaborator.

        :param h5_file: Path to the HDF5 file.
        :type h5_file: str
        :param mode: Default PyTables open mode.
        :type mode: str
        '''

        # Initialize the parent H5Repository.
        super().__init__(h5_file=h5_file, mode=mode)

        # Association rows share the file but not the node mixin.
        self.associations = DocumentTagTableRepository(h5_file=h5_file, mode=mode)

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a tag exists by ID.

        :param id: The tag identifier.
        :type id: str
        :return: True if the tag exists, otherwise False.
        :rtype: bool
        '''

        # Delegate to the NodeRepository mixin; a missing file is False.
        return NodeRepository.exists(self, id=id)

    # * method: get
    def get(self, id: str) -> Optional[TagAggregate]:
        '''
        Retrieve a tag by ID.

        :param id: The tag identifier.
        :type id: str
        :return: The tag aggregate, or None if not found.
        :rtype: TagAggregate | None
        '''

        # A missing file must not be created by a read.
        if not self.file_exists():
            return None

        # Resolve the HDF5 group path for the tag.
        group_path = self.resolve_node_path(id=id)

        # Read attributes from the group node.
        with self.client() as h5:

            # Return None if the group does not exist.
            if not h5.node_exists(group_path):
                return None

            # Load the node attributes.
            attrs = h5.get_node_attrs(group_path)

        # Map the attributes to a tag aggregate, injecting the id.
        return TagNodeObject.from_attrs(attrs, id=id).map()

    # * method: list
    def list(self) -> List[TagAggregate]:
        '''
        List all tags.

        :return: A list of tag aggregates.
        :rtype: List[TagAggregate]
        '''

        # Collect all tag aggregates.
        tags: List[TagAggregate] = []

        # A missing file yields an empty list and must not be created.
        if not self.file_exists():
            return tags

        with self.client() as h5:

            # Return empty if the root group does not exist.
            if not h5.node_exists(TAGS_ROOT):
                return tags

            # Iterate over child groups under the tags root.
            root = h5.get_group(TAGS_ROOT)
            for child in root._v_children.values():

                # Read attributes from each child group.
                attrs = h5.get_node_attrs(child._v_pathname)
                tag_id = child._v_name

                # Map to aggregate and collect.
                tags.append(
                    TagNodeObject.from_attrs(attrs, id=tag_id).map()
                )

        # Return the collected tags.
        return tags

    # * method: save
    def save(self, tag: TagAggregate) -> None:
        '''
        Save or update a tag.

        :param tag: The tag aggregate to save.
        :type tag: TagAggregate
        :return: None
        :rtype: None
        '''

        # Convert the aggregate to a node object and delegate to the mixin,
        # which creates the group when absent and writes the attributes.
        node_obj = TagNodeObject.from_model(tag)
        NodeRepository.save(self, node_obj, id=tag.id)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete a tag label by ID. This operation is idempotent.

        Does not clear associations. Callers that must refuse while a
        document still carries the tag check carriers before calling this.

        :param id: The tag identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # A missing file has nothing to delete and must not be created.
        if not self.file_exists():
            return

        # Resolve the HDF5 group path for the tag.
        group_path = self.resolve_node_path(id=id)

        with self.client() as h5:

            # Remove the group and its contents; a missing node is a no-op.
            self.remove_node(h5, group_path, recursive=True)

    # * method: _pair_condition
    def _pair_condition(self, document_id: str, tag_id: str) -> str:
        '''
        Build the PyTables condition for one document–tag pair.

        :param document_id: The document identifier.
        :type document_id: str
        :param tag_id: The tag identifier.
        :type tag_id: str
        :return: A condition matching that pair.
        :rtype: str
        '''

        # Match both columns. Bytes literals match StringCol storage.
        return f'(document_id == b"{document_id}") & (tag_id == b"{tag_id}")'

    # * method: tag_document
    def tag_document(self, document_id: str, tag_id: str) -> None:
        '''
        Record one document–tag association. Repeating it does not add a row.

        :param document_id: The document identifier.
        :type document_id: str
        :param tag_id: The tag identifier.
        :type tag_id: str
        :return: None
        :rtype: None
        '''

        # A second write of the same pair is a no-op.
        condition = self._pair_condition(document_id, tag_id)
        if self.associations.exists(condition):
            return

        # Append the single association row.
        self.associations.save(DocumentTagTableObject(
            document_id=document_id,
            tag_id=tag_id,
        ))

    # * method: untag_document
    def untag_document(self, document_id: str, tag_id: str) -> None:
        '''
        Remove one document–tag association if it is present.

        :param document_id: The document identifier.
        :type document_id: str
        :param tag_id: The tag identifier.
        :type tag_id: str
        :return: None
        :rtype: None
        '''

        # Absent pairs, and a missing table, are a success.
        condition = self._pair_condition(document_id, tag_id)
        if self.associations.exists(condition):
            self.associations.delete(condition)

    # * method: list_document_ids
    def list_document_ids(self, tag_id: str) -> List[str]:
        '''
        List document identifiers that carry a tag.

        :param tag_id: The tag identifier.
        :type tag_id: str
        :return: Carrier document identifiers, without duplicates.
        :rtype: List[str]
        '''

        # Read association rows. A missing table is an empty list.
        rows = self.associations.list(f'(tag_id == b"{tag_id}")')

        # Drop a repeated pair if one was ever stored.
        carriers: List[str] = []
        for row in rows:
            if row.document_id not in carriers:
                carriers.append(row.document_id)

        # Return the carrier identifiers.
        return carriers

    # * method: list_tags_for_document
    def list_tags_for_document(self, document_id: str) -> List[TagAggregate]:
        '''
        List the tags a document carries.

        A missing tag label is skipped. The association row is still a
        carrier for ``list_document_ids``.

        :param document_id: The document identifier.
        :type document_id: str
        :return: Tag aggregates the document carries.
        :rtype: List[TagAggregate]
        '''

        # Read association rows for this document.
        rows = self.associations.list(f'(document_id == b"{document_id}")')

        # Resolve each tag label. Skip a label that is already gone.
        tags: List[TagAggregate] = []
        seen = set()
        for row in rows:
            if row.tag_id in seen:
                continue
            seen.add(row.tag_id)
            tag = self.get(row.tag_id)
            if tag is not None:
                tags.append(tag)

        # Return the resolved tags.
        return tags

    # * method: clear_document
    def clear_document(self, document_id: str) -> None:
        '''
        Remove every association for a document. Idempotent when none exist.

        :param document_id: The document identifier.
        :type document_id: str
        :return: None
        :rtype: None
        '''

        # A missing table or an untagged document is a no-op.
        condition = f'(document_id == b"{document_id}")'
        if self.associations.exists(condition):
            self.associations.delete(condition)
