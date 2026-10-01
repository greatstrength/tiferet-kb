"""tiferet_kb Document Mappers"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

# ** infra
import tables
from pydantic import Field

# ** app
from tiferet.mappers import Aggregate
from tiferet_h5.mappers import NodeObject, TableObject

from ..domain.document import Document, DocumentProperty, DocumentSection, SectionRevision
from ..domain.segment import Paragraph

# *** mappers

# ** mapper: document_section_aggregate
class DocumentSectionAggregate(DocumentSection, Aggregate):
    '''
    A mutable aggregate representation of a document section.
    '''

    # * method: rename
    def rename(self, title: str) -> None:
        '''
        Rename the section.

        :param title: The new section title.
        :type title: str
        :return: None
        :rtype: None
        '''

        # Update the title and timestamp.
        self.title = title
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_paragraphs
    def set_paragraphs(self, paragraphs: List[Paragraph]) -> None:
        '''
        Replace the section's paragraphs with a new list.

        :param paragraphs: The new paragraphs.
        :type paragraphs: List[Paragraph]
        :return: None
        :rtype: None
        '''

        # Update the paragraphs and timestamp.
        self.paragraphs = paragraphs
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_heading_level
    def set_heading_level(self, heading_level: int) -> None:
        '''
        Set the section heading level.

        :param heading_level: The new heading level (1-6).
        :type heading_level: int
        :return: None
        :rtype: None
        '''

        # Update the heading level and timestamp.
        self.heading_level = heading_level
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_icon
    def set_icon(self, icon: Optional[str]) -> None:
        '''
        Set the section icon.

        :param icon: The new icon identifier, or None to clear.
        :type icon: str | None
        :return: None
        :rtype: None
        '''

        # Update the icon and timestamp.
        self.icon = icon
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_content_type
    def set_content_type(self, content_type: str) -> None:
        '''
        Set the section content type.

        :param content_type: The new content type.
        :type content_type: str
        :return: None
        :rtype: None
        '''

        # Update the content type and timestamp.
        self.content_type = content_type
        self.updated_at = datetime.now(timezone.utc).isoformat()

# ** mapper: document_aggregate
class DocumentAggregate(Document, Aggregate):
    '''
    A mutable aggregate representation of a knowledge base document.
    '''

    # * attribute: sections
    sections: List[DocumentSectionAggregate] = Field(
        default_factory=list,
        description='Ordered list of mutable document section aggregates.',
    )

    # * method: rename
    def rename(self, title: str) -> None:
        '''
        Rename the document.

        :param title: The new document title.
        :type title: str
        :return: None
        :rtype: None
        '''

        # Update the title and timestamp.
        self.title = title
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_status
    def set_status(self, status: str) -> None:
        '''
        Set the document status.

        :param status: The new status (draft, published, archived).
        :type status: str
        :return: None
        :rtype: None
        '''

        # Update the status and timestamp.
        self.status = status
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_folder
    def set_folder(self, folder_id: str | None) -> None:
        '''
        Set the document's folder.

        :param folder_id: The folder identifier, or None to unfile.
        :type folder_id: str | None
        :return: None
        :rtype: None
        '''

        # Update the folder and timestamp.
        self.folder_id = folder_id
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_category
    def set_category(self, category_id: str | None) -> None:
        '''
        Set the document's category.

        :param category_id: The category identifier, or None to uncategorize.
        :type category_id: str | None
        :return: None
        :rtype: None
        '''

        # Update the category and timestamp.
        self.category_id = category_id
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_visibility
    def set_visibility(self, visibility: str) -> None:
        '''
        Set the document visibility label.

        :param visibility: The visibility token (public, private, or restricted).
        :type visibility: str
        :return: None
        :rtype: None
        '''

        # Update the visibility and timestamp.
        self.visibility = visibility
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_owner
    def set_owner(self, owner_id: str | None) -> None:
        '''
        Set or clear the document owner.

        :param owner_id: The opaque owner identifier, or None to clear.
        :type owner_id: str | None
        :return: None
        :rtype: None
        '''

        # Update the owner and timestamp.
        self.owner_id = owner_id
        self.updated_at = datetime.now(timezone.utc).isoformat()

# ** mapper: document_table_object
class DocumentTableObject(TableObject):
    '''
    An HDF5 table-row representation of a document header.

    Stored as rows in ``/kb/documents/documents``.  The ``sections``
    field is excluded — sections are group nodes with a nested ``segments``
    table under ``/kb/documents/<document_id>/sections/``.
    '''

    # * attribute: id
    id: str = Field(default='', description='Document UUID.')

    # * attribute: title
    title: str = Field(default='', description='Document title.')

    # * attribute: category_id
    category_id: str = Field(default='', description='Category identifier.')

    # * attribute: template_id
    template_id: str = Field(default='', description='Template identifier.')

    # * attribute: folder_id
    folder_id: str = Field(default='', description='Folder identifier.')

    # * attribute: status
    status: str = Field(default='draft', description='Document status.')

    # * attribute: visibility
    visibility: str = Field(default='public', description='Access label. Empty reads as public.')

    # * attribute: owner_id
    owner_id: str = Field(default='', description='Opaque owner identifier. Empty reads as absent.')

    # * attribute: created_at
    created_at: str = Field(default='', description='ISO 8601 creation timestamp.')

    # * attribute: updated_at
    updated_at: str = Field(default='', description='ISO 8601 last-updated timestamp.')

    # * attribute: _H5_TYPES
    _H5_TYPES: ClassVar[Dict[str, Any]] = {
        'id':          tables.StringCol(64),
        'title':       tables.StringCol(512),
        'category_id': tables.StringCol(64),
        'template_id': tables.StringCol(64),
        'folder_id':   tables.StringCol(64),
        'status':      tables.StringCol(32),
        'visibility':  tables.StringCol(32),
        'owner_id':    tables.StringCol(64),
        'created_at':  tables.StringCol(32),
        'updated_at':  tables.StringCol(32),
    }

    # * method: map
    def map(self, **overrides) -> DocumentAggregate:
        '''
        Map the table object data to a document aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new document aggregate (without sections).
        :rtype: DocumentAggregate
        '''

        # Serialize and construct the aggregate, converting empty strings to None.
        data = self.to_primitive()
        for field in ('category_id', 'template_id', 'folder_id', 'owner_id'):
            if data.get(field) == '':
                data[field] = None

        # A blank visibility column reads as public, including a pre-change row.
        visibility = data.get('visibility')
        if not isinstance(visibility, str) or not visibility.strip():
            data['visibility'] = 'public'
        data.update(overrides)

        # Return the constructed aggregate.
        return DocumentAggregate(**data)

    # * method: from_model
    @classmethod
    def from_model(cls, document: Document, **overrides) -> 'DocumentTableObject':
        '''
        Create a DocumentTableObject from a Document model.

        :param document: The document model to copy from.
        :type document: Document
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new DocumentTableObject.
        :rtype: DocumentTableObject
        '''

        # Dump the header only. Sections and properties are stored apart from this row.
        data = document.model_dump(by_alias=False, exclude={'sections', 'properties'})
        for field in ('category_id', 'template_id', 'folder_id', 'owner_id'):
            if data.get(field) is None:
                data[field] = ''

        # Persist the read default when the aggregate has no visibility token.
        if not data.get('visibility'):
            data['visibility'] = 'public'
        data.update(overrides)

        # Construct and return the table object.
        return cls.model_validate(data)

# ** mapper: document_section_node_object
class DocumentSectionNodeObject(NodeObject):
    '''
    An HDF5 node-attribute representation of a document section.

    Section metadata is stored as attributes on an HDF5 group node
    at ``/kb/documents/<doc_id>/sections/<section_id>``. The ``paragraphs``
    field is excluded — paragraph and segment data live in a flat
    ``segments`` table inside the section group.
    '''

    # * attribute: id
    id: str = Field(default='', description='Section UUID.')

    # * attribute: document_id
    document_id: str = Field(default='', description='Parent document UUID.')

    # * attribute: title
    title: str = Field(default='', description='Section heading.')

    # * attribute: heading_level
    heading_level: int = Field(default=2, description='Heading level.')

    # * attribute: icon
    icon: str = Field(default='', description='Icon identifier.')

    # * attribute: content_type
    content_type: str = Field(default='markdown', description='Content type.')

    # * attribute: position
    position: int = Field(default=0, description='Ordering position.')

    # * attribute: created_at
    created_at: str = Field(default='', description='ISO 8601 creation timestamp.')

    # * attribute: updated_at
    updated_at: str = Field(default='', description='ISO 8601 last-updated timestamp.')

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_h5.attrs': {
            'by_alias': True,
            'exclude': {'id', 'document_id', 'paragraphs'},
        },
    }

    # * method: map
    def map(self, **overrides) -> DocumentSectionAggregate:
        '''
        Map the node object data to a document section aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new document section aggregate.
        :rtype: DocumentSectionAggregate
        '''

        # Serialize and clean empty icon.
        data = self.to_primitive(role='to_model')
        if data.get('icon') == '':
            data['icon'] = None
        data.update(overrides)

        # Return the constructed aggregate.
        return DocumentSectionAggregate(**data)

    # * method: from_model
    @classmethod
    def from_model(cls, section: DocumentSection, **overrides) -> 'DocumentSectionNodeObject':
        '''
        Create a DocumentSectionNodeObject from a DocumentSection model.

        :param section: The section model to copy from.
        :type section: DocumentSection
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new DocumentSectionNodeObject.
        :rtype: DocumentSectionNodeObject
        '''

        # Dump the model, excluding paragraphs (stored separately).
        data = section.model_dump(by_alias=False, exclude={'paragraphs'})
        if data.get('icon') is None:
            data['icon'] = ''
        data.update(overrides)

        # Construct and return the node object.
        return cls.model_validate(data)

# ** mapper: document_property_table_object
class DocumentPropertyTableObject(TableObject):
    '''
    An HDF5 table-row representation of one document property.

    Stored as rows in ``/kb/documents/document_properties``, sibling to the
    header table. One value column per type so a read does not guess the
    type from text. Only the column named by ``value_type`` is meaningful.
    '''

    # * attribute: document_id
    document_id: str = Field(default='', description='Parent document UUID.')

    # * attribute: name
    name: str = Field(default='', description='Stored property name.')

    # * attribute: value_type
    value_type: str = Field(default='', description='Declared value type.')

    # * attribute: value_string
    value_string: str = Field(default='', description='String value. Meaningful only when value_type is string.')

    # * attribute: value_number
    value_number: float = Field(default=0.0, description='Number value. Meaningful only when value_type is number.')

    # * attribute: value_boolean
    value_boolean: bool = Field(default=False, description='Boolean value. Meaningful only when value_type is boolean.')

    # * attribute: _H5_TYPES
    _H5_TYPES: ClassVar[Dict[str, Any]] = {
        'document_id': tables.StringCol(64),
        'name': tables.StringCol(1024),
        'value_type': tables.StringCol(16),
        'value_string': tables.StringCol(4096),
        'value_number': tables.Float64Col(),
        'value_boolean': tables.BoolCol(),
    }

    # * method: to_property
    def to_property(self) -> DocumentProperty:
        '''
        Rebuild the domain property from the column that matches ``value_type``.

        :return: The property, with no cross-type coercion.
        :rtype: DocumentProperty
        '''

        # Read only the column the stored type names.
        if self.value_type == 'number':
            value = self.value_number
        elif self.value_type == 'boolean':
            value = self.value_boolean
        else:
            value = self.value_string

        # Return the domain property.
        return DocumentProperty(
            document_id=self.document_id,
            name=self.name,
            value=value,
            value_type=self.value_type,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, prop: DocumentProperty, **overrides) -> 'DocumentPropertyTableObject':
        '''
        Create a table row from a document property.

        The unused typed columns stay at their empty defaults so a later read
        cannot mistake them for the stored value.

        :param prop: The property to store.
        :type prop: DocumentProperty
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new table object.
        :rtype: DocumentPropertyTableObject
        '''

        # Start from empty typed columns, then fill the one that matches.
        data = {
            'document_id': prop.document_id,
            'name': prop.name,
            'value_type': prop.value_type,
            'value_string': '',
            'value_number': 0.0,
            'value_boolean': False,
        }
        if prop.value_type == 'string':
            data['value_string'] = prop.value
        elif prop.value_type == 'number':
            data['value_number'] = float(prop.value)
        else:
            data['value_boolean'] = bool(prop.value)
        data.update(overrides)

        # Construct and return the table object.
        return cls.model_validate(data)

# ** mapper: section_revision_node_object
class SectionRevisionNodeObject(NodeObject):
    '''
    HDF5 node-attribute header for one section revision.

    The number, heading, content type, and snapshot time live on the
    revision group. Passages live in a nested segments table of the same
    row shape as the live section, not in a content string.
    '''

    # * attribute: document_id
    document_id: str = Field(default='', description='Parent document UUID.')

    # * attribute: section_id
    section_id: str = Field(default='', description='Parent section UUID.')

    # * attribute: number
    number: int = Field(default=1, description='Revision number within the section.')

    # * attribute: created_at
    created_at: str = Field(default='', description='UTC ISO 8601 snapshot time.')

    # * attribute: title
    title: str = Field(default='', description='Section heading at snapshot time.')

    # * attribute: content_type
    content_type: str = Field(default='markdown', description='Content type at snapshot time.')

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_h5.attrs': {
            'by_alias': True,
            'exclude': {'document_id', 'section_id'},
        },
    }

    # * method: map
    def map(self, **overrides) -> SectionRevision:
        '''
        Map the node attributes to a read-only section revision.

        :param overrides: Additional keyword arguments, including paragraphs.
        :type overrides: dict
        :return: A new section revision.
        :rtype: SectionRevision
        '''

        # Serialize the header and apply paragraph overrides.
        data = self.to_primitive(role='to_model')
        data.update(overrides)

        # Return the read-only revision. It is not an aggregate.
        return SectionRevision(**data)
