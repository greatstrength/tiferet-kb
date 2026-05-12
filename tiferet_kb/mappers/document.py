"""tiferet_kb Document Mappers"""

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

from ..domain.document import Document, DocumentSection

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

    # * method: set_content
    def set_content(self, content: str) -> None:
        '''
        Set the section content.

        :param content: The new content.
        :type content: str
        :return: None
        :rtype: None
        '''

        # Update the content and timestamp.
        self.content = content
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


# ** mapper: document_table_object
class DocumentTableObject(TableObject):
    '''
    An HDF5 table-row representation of a document header.

    Stored as rows in ``/kb/documents/documents``.  The ``sections``
    field is excluded — sections are stored in a separate table.
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
        for field in ('category_id', 'template_id', 'folder_id'):
            if data.get(field) == '':
                data[field] = None
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

        # Dump the model, excluding sections (stored separately), and replace None with ''.
        data = document.model_dump(by_alias=False, exclude={'sections'})
        for field in ('category_id', 'template_id', 'folder_id'):
            if data.get(field) is None:
                data[field] = ''
        data.update(overrides)

        # Construct and return the table object.
        return cls.model_validate(data)


# ** mapper: document_section_table_object
class DocumentSectionTableObject(TableObject):
    '''
    An HDF5 table-row representation of a document section.

    Stored as rows in ``/kb/documents/document_sections``.
    '''

    # * attribute: id
    id: str = Field(default='', description='Section UUID.')

    # * attribute: document_id
    document_id: str = Field(default='', description='Parent document UUID.')

    # * attribute: title
    title: str = Field(default='', description='Section heading.')

    # * attribute: content_type
    content_type: str = Field(default='', description='Content type.')

    # * attribute: content
    content: str = Field(default='', description='Raw section content.')

    # * attribute: position
    position: int = Field(default=0, description='Ordering position.')

    # * attribute: created_at
    created_at: str = Field(default='', description='ISO 8601 creation timestamp.')

    # * attribute: updated_at
    updated_at: str = Field(default='', description='ISO 8601 last-updated timestamp.')

    # * attribute: _H5_TYPES
    _H5_TYPES: ClassVar[Dict[str, Any]] = {
        'id':           tables.StringCol(64),
        'document_id':  tables.StringCol(64),
        'title':        tables.StringCol(512),
        'content_type': tables.StringCol(32),
        'content':      tables.StringCol(65536),
        'position':     tables.Int32Col(),
        'created_at':   tables.StringCol(32),
        'updated_at':   tables.StringCol(32),
    }

    # * method: map
    def map(self, **overrides) -> DocumentSectionAggregate:
        '''
        Map the table object data to a document section aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new document section aggregate.
        :rtype: DocumentSectionAggregate
        '''

        # Serialize and construct the aggregate.
        data = self.to_primitive()
        data.update(overrides)

        # Return the constructed aggregate.
        return DocumentSectionAggregate(**data)

    # * method: from_model
    @classmethod
    def from_model(cls, section: DocumentSection, **overrides) -> 'DocumentSectionTableObject':
        '''
        Create a DocumentSectionTableObject from a DocumentSection model.

        :param section: The section model to copy from.
        :type section: DocumentSection
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new DocumentSectionTableObject.
        :rtype: DocumentSectionTableObject
        '''

        # Dump the model and construct the table object.
        data = section.model_dump(by_alias=False)
        data.update(overrides)

        # Construct and return the table object.
        return cls.model_validate(data)
