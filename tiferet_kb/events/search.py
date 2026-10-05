"""tiferet_kb Search Events"""

# *** imports

# ** core
from typing import Any, Dict, List, Optional

# ** app
from tiferet.assets.error import COMMAND_PARAMETER_REQUIRED_ID
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

    # * method: require_present
    def require_present(self, name: str, value: Any) -> None:
        '''
        Raise when a required value was omitted or is None.

        A blank string is present. It is forwarded, and it is not a missing
        parameter. The existing command-parameter error is reused. No search
        error code is added.

        :param name: The parameter name.
        :type name: str
        :param value: The value passed to execute.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # None is absent. An empty string is a query that matches nothing.
        if value is None:
            self.raise_error(
                COMMAND_PARAMETER_REQUIRED_ID,
                message=f'Required parameters missing for {self.__class__.__name__}.',
                parameters=[name],
                command=self.__class__.__name__,
            )

# ** event: search_keyword_sections
class SearchKeywordSections(SearchEvent):
    '''
    Event to rank sections by the words in their rendered bodies.

    The caller supplies the query string. A blank string is forwarded and
    matches nothing. An omitted query still fails. This event does not stem,
    expand, or embed the query. Filters narrow placement; they do not change
    the score.
    '''

    # * method: execute
    def execute(self,
            query: Optional[str] = None,
            limit: int = 5,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
            document_id: Optional[str] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Search sections by keyword.

        :param query: The query string. A blank string is forwarded.
        :type query: str | None
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

        # A blank query is a query. Only absence raises.
        self.require_present('query', query)

        # Always forward the filters, including None. Forward a blank query too.
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

    The caller supplies both the words and the query vector. A blank query
    is forwarded, so the embedding side is not dropped. This domain does not
    build the vector, and the composed score is not either side's score.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['query_embedding'])
    def execute(self,
            query: Optional[str] = None,
            query_embedding: list = None,
            limit: int = 5,
            folder_id: Optional[str] = None,
            category_id: Optional[str] = None,
            document_id: Optional[str] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Search sections by reciprocal rank fusion of keyword and embedding hits.

        :param query: The query string. A blank string is forwarded.
        :type query: str | None
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

        # A blank query still fuses. Only an absent query raises.
        self.require_present('query', query)

        # Always forward the filters, including None. Do not pass a model name.
        return self.document_service.search_composed(
            query=query,
            query_embedding=query_embedding,
            limit=limit,
            folder_id=folder_id,
            category_id=category_id,
            document_id=document_id,
        )
