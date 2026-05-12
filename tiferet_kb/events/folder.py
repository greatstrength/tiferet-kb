"""tiferet_kb Folder Events"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** app
from tiferet.events import DomainEvent

from ..assets import constants as const
from ..domain.folder import Folder
from ..interfaces.folder import FolderService
from ..interfaces.document import DocumentService
from ..mappers.folder import FolderAggregate

# *** events

# ** event: add_folder
class AddFolder(DomainEvent):
    '''
    Event to create a new knowledge base folder.
    '''

    # * attribute: folder_service
    folder_service: FolderService

    # * init
    def __init__(self, folder_service: FolderService):
        '''
        Initialize the AddFolder event.

        :param folder_service: The folder service for persistence.
        :type folder_service: FolderService
        '''

        # Set the folder service dependency.
        self.folder_service = folder_service

    # * method: execute
    @DomainEvent.parameters_required(['name'])
    def execute(self,
            name: str,
            id: str | None = None,
            parent_id: str | None = None,
            path: str | None = None,
            **kwargs,
        ) -> Folder:
        '''
        Create a new folder.

        :param name: The folder name.
        :type name: str
        :param id: Optional explicit UUID.
        :type id: str | None
        :param parent_id: Optional parent folder ID for nesting.
        :type parent_id: str | None
        :param path: Optional explicit path.
        :type path: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created folder.
        :rtype: Folder
        '''

        # Build the aggregate construction kwargs.
        folder_kwargs = dict(name=name)
        if id:
            folder_kwargs['id'] = id
        if parent_id:
            folder_kwargs['parent_id'] = parent_id

        # If parent_id is provided, build the path from the parent.
        if parent_id and not path:
            parent = self.folder_service.get(parent_id)
            if parent:
                folder_kwargs['path'] = f'{parent.path}/{name}'
        if path:
            folder_kwargs['path'] = path

        # Create the folder aggregate.
        folder = FolderAggregate(**folder_kwargs)

        # Verify no duplicate.
        self.verify(
            expression=not self.folder_service.exists(folder.id),
            error_code=const.KB_FOLDER_ALREADY_EXISTS_ID,
            message=f'Folder with ID {folder.id} already exists.',
            id=folder.id,
        )

        # Persist the folder.
        self.folder_service.save(folder)

        # Return the created folder.
        return folder


# ** event: get_folder
class GetFolder(DomainEvent):
    '''
    Event to retrieve a folder by its identifier.
    '''

    # * attribute: folder_service
    folder_service: FolderService

    # * init
    def __init__(self, folder_service: FolderService):
        '''
        Initialize the GetFolder event.

        :param folder_service: The folder service for retrieval.
        :type folder_service: FolderService
        '''

        # Set the folder service dependency.
        self.folder_service = folder_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> Folder:
        '''
        Retrieve a folder by ID.

        :param id: The folder identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The retrieved folder.
        :rtype: Folder
        '''

        # Retrieve the folder.
        folder = self.folder_service.get(id)

        # Verify existence.
        self.verify(
            expression=folder is not None,
            error_code=const.KB_FOLDER_NOT_FOUND_ID,
            folder_id=id,
        )

        # Return the folder.
        return folder


# ** event: list_folder_contents
class ListFolderContents(DomainEvent):
    '''
    Event to list child folders and documents within a folder.
    '''

    # * attribute: folder_service
    folder_service: FolderService

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, folder_service: FolderService, document_service: DocumentService):
        '''
        Initialize the ListFolderContents event.

        :param folder_service: The folder service for listing child folders.
        :type folder_service: FolderService
        :param document_service: The document service for listing documents.
        :type document_service: DocumentService
        '''

        # Set dependencies.
        self.folder_service = folder_service
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['folder_id'])
    def execute(self, folder_id: str, **kwargs) -> Dict[str, List]:
        '''
        List child folders and documents within a folder.

        :param folder_id: The folder identifier.
        :type folder_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A dict with 'folders' and 'documents' keys.
        :rtype: Dict[str, List]
        '''

        # Verify the folder exists.
        self.verify(
            expression=self.folder_service.exists(folder_id),
            error_code=const.KB_FOLDER_NOT_FOUND_ID,
            folder_id=folder_id,
        )

        # List child folders and documents.
        child_folders = self.folder_service.list(parent_id=folder_id)
        documents = self.document_service.list(folder_id=folder_id)

        # Return the combined results.
        return {
            'folders': child_folders,
            'documents': documents,
        }


# ** event: move_folder
class MoveFolder(DomainEvent):
    '''
    Event to move a folder to a new parent.
    '''

    # * attribute: folder_service
    folder_service: FolderService

    # * init
    def __init__(self, folder_service: FolderService):
        '''
        Initialize the MoveFolder event.

        :param folder_service: The folder service for persistence.
        :type folder_service: FolderService
        '''

        # Set the folder service dependency.
        self.folder_service = folder_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self,
            id: str,
            new_parent_id: str | None = None,
            **kwargs,
        ) -> Folder:
        '''
        Move a folder to a new parent.

        :param id: The folder identifier to move.
        :type id: str
        :param new_parent_id: The new parent folder ID, or None for root.
        :type new_parent_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The moved folder.
        :rtype: Folder
        '''

        # Retrieve the folder.
        folder = self.folder_service.get(id)
        self.verify(
            expression=folder is not None,
            error_code=const.KB_FOLDER_NOT_FOUND_ID,
            folder_id=id,
        )

        # Prevent circular reference.
        if new_parent_id:
            self.verify(
                expression=new_parent_id != id,
                error_code=const.KB_FOLDER_CIRCULAR_REFERENCE_ID,
                message='A folder cannot be its own parent.',
                folder_id=id,
            )

        # Build the new path.
        if new_parent_id:
            parent = self.folder_service.get(new_parent_id)
            self.verify(
                expression=parent is not None,
                error_code=const.KB_FOLDER_NOT_FOUND_ID,
                folder_id=new_parent_id,
            )
            new_path = f'{parent.path}/{folder.name}'
        else:
            new_path = f'/{folder.name}'

        # Update the folder.
        folder.set_parent(new_parent_id)
        folder.update_path(new_path)

        # Persist via move (updates parent_id attr).
        self.folder_service.move(id, new_parent_id)
        self.folder_service.save(folder)

        # Return the moved folder.
        return folder


# ** event: move_document
class MoveDocument(DomainEvent):
    '''
    Event to move a document to a different folder.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the MoveDocument event.

        :param document_service: The document service for persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['document_id'])
    def execute(self,
            document_id: str,
            folder_id: str | None = None,
            **kwargs,
        ) -> str:
        '''
        Move a document to a different folder.

        :param document_id: The document identifier.
        :type document_id: str
        :param folder_id: The target folder ID, or None to unfile.
        :type folder_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document identifier.
        :rtype: str
        '''

        # Retrieve the document.
        document = self.document_service.get(document_id)
        self.verify(
            expression=document is not None,
            error_code=const.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=document_id,
        )

        # Update the folder assignment.
        document.set_folder(folder_id)

        # Persist the updated document.
        self.document_service.save(document)

        # Return the document identifier.
        return document_id


# ** event: remove_folder
class RemoveFolder(DomainEvent):
    '''
    Event to remove a folder by ID (idempotent).

    Documents within the folder are unfiled (folder_id set to None)
    rather than deleted.
    '''

    # * attribute: folder_service
    folder_service: FolderService

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, folder_service: FolderService, document_service: DocumentService):
        '''
        Initialize the RemoveFolder event.

        :param folder_service: The folder service for deletion.
        :type folder_service: FolderService
        :param document_service: The document service for unfiling documents.
        :type document_service: DocumentService
        '''

        # Set dependencies.
        self.folder_service = folder_service
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a folder by ID. Documents in the folder are unfiled.

        :param id: The folder identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The removed folder ID.
        :rtype: str
        '''

        # Unfile all documents in this folder.
        documents = self.document_service.list(folder_id=id)
        for doc in documents:
            doc.set_folder(None)
            self.document_service.save(doc)

        # Delete the folder (idempotent).
        self.folder_service.delete(id)

        # Return the folder identifier.
        return id
