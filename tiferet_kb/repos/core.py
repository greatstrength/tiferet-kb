"""tiferet_kb Core H5 Repositories"""

# *** imports

# ** core
from typing import Any, Type

# ** app
from tiferet_h5.mappers import TableObject
from tiferet_h5.repos import H5Repository, NodeRepository, TableRepository

# *** constants

# ** constant: schema_version_attr
SCHEMA_VERSION_ATTR = 'schema_version'

# *** classes

# ** class: kb_node_repository
class KBNodeRepository(NodeRepository, H5Repository):
    '''
    Node repository for tiferet-kb HDF5 stores.

    Extends tiferet-h5's ``NodeRepository`` (beside ``H5Repository``) with
    ``remove_node``, because ``H5Client`` in tiferet-h5 1.x has no
    node-removal method and ``NodeRepository`` has no ``delete``.  Do not also
    compose ``TableRepository`` on the same class; ``save``, ``get``, and
    ``exists`` collide.
    '''

    # * method: remove_node
    def remove_node(self, h5: Any, path: str, recursive: bool = False) -> None:
        '''
        Remove a group or array node through an already-open client.

        This is the only place in tiferet_kb that calls ``h5file.remove_node``.
        A missing node is not an error.  Row removal is not handled here; use
        ``H5Client.remove_rows`` or ``TableRepository.delete`` for rows.

        :param h5: The open H5Client instance.
        :type h5: H5Client
        :param path: The absolute HDF5 path of the node to remove.
        :type path: str
        :param recursive: True to remove a group and its children; arrays and
            tables use the default.
        :type recursive: bool
        :return: None
        :rtype: None
        '''

        # Return silently when the node is absent (idempotent).
        if not h5.node_exists(path):
            return

        # Remove the node through the underlying PyTables file.
        h5.h5file.remove_node(path, recursive=recursive)

# ** class: kb_table_repository
class KBTableRepository(TableRepository, H5Repository):
    '''
    Table repository for tiferet-kb HDF5 stores.

    Extends tiferet-h5's ``TableRepository`` (beside ``H5Repository``) with
    ``ensure_table``, which creates a table on an already-open client and
    stamps ``schema_version`` the same way ``TableRepository.save`` does.  Do
    not also compose ``NodeRepository`` on the same class; ``save``, ``get``,
    and ``exists`` collide.
    '''

    # * method: ensure_table
    def ensure_table(self,
            h5: Any,
            path: str,
            table_cls: Type[TableObject],
            title: str = '',
        ) -> Any:
        '''
        Return the table at ``path``, creating it and stamping ``schema_version`` on create.

        The stamp is ``table_cls.schema_fingerprint()`` and is written only
        when this call creates the table.  An existing table, with or without
        a stamp, is returned unchanged and is not checked;
        ``H5Client.assert_schema`` is the opt-in check.

        :param h5: The open H5Client instance.
        :type h5: H5Client
        :param path: The absolute HDF5 path of the table.
        :type path: str
        :param table_cls: The TableObject class declaring the table schema.
        :type table_cls: Type[TableObject]
        :param title: The title used when the table is created.
        :type title: str
        :return: The PyTables table.
        :rtype: Any
        '''

        # Return the existing table without touching its stamp.
        if h5.node_exists(path):
            return h5.get_table(path)

        # Create the table from the declared description.
        table = h5.create_table(path, table_cls.get_description(), title=title)

        # Stamp the schema fingerprint on first create only.
        h5.set_node_attr(path, SCHEMA_VERSION_ATTR, table_cls.schema_fingerprint())

        # Return the newly created table.
        return table
