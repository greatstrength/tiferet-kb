"""tiferet_kb Search Events"""

# *** imports

# ** core
from typing import Dict, List, Optional

# ** app
from tiferet.events import DomainEvent

from ..interfaces.document import DocumentService

# *** events

# ** event: search_event
class SearchEvent(DomainEvent):
    '''
    Base event for retrieving sections by the words written in them.

    Keyword search and composed retrieval share the document service. They
    do not open a second repository, and they do not compute an embedding.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * init
    def __init__(self, document_service: DocumentService) -> None:
        '''
        Initialize the search event.

        :param document_service: The document service for retrieval.
        :type document_service: DocumentService
        '''

        # Set the document service dependency.
        self.document_service = document_service

# ** event: search_keyword_sections
class SearchKeywordSections(SearchEvent):
    '''
    Event to rank sections by the words in their rendered bodies.

    The caller supplies the query string. This event does not stem, expand,
    or embed it. Filters narrow placement; they do not change the score.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['query'])
    def execute(self,
            query: str,
            limit: int = 5,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
            document_id: Optional[str] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Search sections by keyword.

        :param query: The query string. Tokenized the same way as a body.
        :type query: str
        :param limit: Maximum number of hits. Applied after filters.
        :type limit: int
        :param folder_id: Optional folder filter. Empty adds no constraint.
        :type folder_id: str | None
        :param category_id: Optional category filter. Empty adds no constraint.
        :type category_id: str | None
        :param document_id: Optional document filter. Omitted means file-wide.
        :type document_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Ranked list of dicts with section_id and score.
        :rtype: List[Dict]
        '''

        # Always forward the filters, including None.
        return self.document_service.search_keyword(
            query=query,
            limit=limit,
            folder_id=folder_id,
            category_id=category_id,
            document_id=document_id,
        )

# ** event: search_composed_sections
class SearchComposedSections(SearchEvent):
    '''
    Event to merge keyword rank with embedding rank for one query.

    The caller supplies both the words and the query vector. This domain
    does not build the vector, and the composed score is not either side's
    score.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['query', 'query_embedding'])
    def execute(self,
            query: str,
            query_embedding: list,
            limit: int = 5,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
            document_id: Optional[str] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Search sections by reciprocal rank fusion of keyword and embedding hits.

        :param query: The query string.
        :type query: str
        :param query_embedding: The caller-supplied query vector.
        :type query_embedding: list
        :param limit: Maximum number of hits. Applied after fusion.
        :type limit: int
        :param folder_id: Optional folder filter. Empty adds no constraint.
        :type folder_id: str | None
        :param category_id: Optional category filter. Empty adds no constraint.
        :type category_id: str | None
        :param document_id: Optional document filter. Omitted means file-wide.
        :type document_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Ranked list of dicts with section_id and fusion score.
        :rtype: List[Dict]
        '''

        # Always forward the filters, including None. Do not pass a model name.
        return self.document_service.search_composed(
            query=query,
            query_embedding=query_embedding,
            limit=limit,
            folder_id=folder_id,
            category_id=category_id,
            document_id=document_id,
        )
