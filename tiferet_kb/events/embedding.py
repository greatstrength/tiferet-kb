"""tiferet_kb Embedding Events"""

# *** imports

# ** core
from typing import Dict, List, Optional

# ** app
from tiferet.events import DomainEvent

from ..assets import constants as const
from ..interfaces.document import DocumentService

# *** events

# ** event: embed_document_sections
class EmbedDocumentSections(DomainEvent):
    '''
    Event to batch-store embedding vectors for a document's sections.

    The caller generates embedding vectors externally (e.g. via an LLM provider)
    and passes them as a dict mapping section_id → embedding vector.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the EmbedDocumentSections event.

        :param document_service: The document service for persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['document_id', 'embeddings', 'model_name'])
    def execute(self,
            document_id: str,
            embeddings: Dict[str, list],
            model_name: str,
            **kwargs,
        ) -> int:
        '''
        Store embedding vectors for one or more sections of a document.

        :param document_id: The parent document identifier.
        :type document_id: str
        :param embeddings: A dict mapping section_id to embedding vector (list of floats).
        :type embeddings: Dict[str, list]
        :param model_name: The name of the embedding model used.
        :type model_name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The number of embeddings stored.
        :rtype: int
        '''

        # Verify the document exists.
        self.verify(
            expression=self.document_service.exists(document_id),
            error_code=const.KB_DOCUMENT_NOT_FOUND_ID,
            document_id=document_id,
        )

        # Retrieve the document's section IDs for validation.
        sections = self.document_service.get_sections(document_id)
        section_id_set = {s.id for s in sections}

        # Verify all provided section IDs belong to the document.
        for section_id in embeddings:
            self.verify(
                expression=section_id in section_id_set,
                error_code=const.KB_DOCUMENT_SECTION_NOT_FOUND_ID,
                section_id=section_id,
                document_id=document_id,
            )

        # Store each embedding.
        count = 0
        for section_id, vector in embeddings.items():
            self.document_service.embed_section(section_id, vector, model_name)
            count += 1

        # Return the number of embeddings stored.
        return count


# ** event: search_similar_sections
class SearchSimilarSections(DomainEvent):
    '''
    Event to search for document sections similar to a query embedding.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the SearchSimilarSections event.

        :param document_service: The document service for search.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['query_embedding'])
    def execute(self,
            query_embedding: list,
            limit: int = 5,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Search for sections similar to the query embedding.

        :param query_embedding: The query embedding vector.
        :type query_embedding: list
        :param limit: Maximum number of results.
        :type limit: int
        :param folder_id: Optional folder filter.
        :type folder_id: str | None
        :param category_id: Optional category filter.
        :type category_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Ranked list of dicts with section_id and score.
        :rtype: List[Dict]
        '''

        # Delegate to the document service.
        return self.document_service.search_similar(
            query_embedding=query_embedding,
            limit=limit,
            folder_id=folder_id,
            category_id=category_id,
        )


# ** event: remove_embedding
class RemoveEmbedding(DomainEvent):
    '''
    Event to remove a section's embedding vector.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService):
        '''
        Initialize the RemoveEmbedding event.

        :param document_service: The document service for persistence.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

    # * method: execute
    @DomainEvent.parameters_required(['section_id'])
    def execute(self, section_id: str, **kwargs) -> str:
        '''
        Remove the embedding for a section.

        :param section_id: The section identifier.
        :type section_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The section identifier.
        :rtype: str
        '''

        # Verify the section has an embedding.
        embedding = self.document_service.get_embedding(section_id)
        self.verify(
            expression=embedding is not None,
            error_code=const.KB_SECTION_NOT_EMBEDDED_ID,
            section_id=section_id,
        )

        # Remove the section's embedding via the service.
        self.document_service.remove_embedding(section_id)

        # Return the section identifier.
        return section_id
