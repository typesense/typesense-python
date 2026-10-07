"""
This module provides the main async client interface for interacting with the Typesense API.

It contains the AsyncClient class, which serves as the entry point for all Typesense operations,
integrating various components like collections, multi-search, keys, aliases, analytics, etc.

Classes:
    Client: The main client class for interacting with Typesense.

Dependencies:
    - typesense.aliases: Provides the AsyncAliases class.
    - typesense.analytics: Provides the AsyncAnalytics class.
    - typesense.api_call: Provides the AsyncApiCall class for making API requests.
    - typesense.collection: Provides the AsyncCollection class.
    - typesense.collections: Provides the AsyncCollections class.
    - typesense.configuration: Provides AsyncConfiguration and ConfigDict types.
    - typesense.conversations_models: Provides the AsyncConversationsModels class.
    - typesense.debug: Provides the AsyncDebug class.
    - typesense.keys: Provides the AsyncKeys class.
    - typesense.metrics: Provides the AsyncMetrics class.
    - typesense.multi_search: Provides the AsyncMultiSearch class.
    - typesense.operations: Provides the AsyncOperations class.
    - typesense.stopwords: Provides the AsyncStopwords class.
    - typesense.types.document: Provides the AsyncDocumentSchema type.

Note: This module uses conditional imports to support both Python 3.11+ and earlier versions.
"""

import sys

from typing_extensions import deprecated

from typesense.types.document import DocumentSchema

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from .aliases import AsyncAliases
from .analytics import AsyncAnalytics
from .analytics_v1 import AsyncAnalyticsV1
from .api_call import AsyncApiCall
from .collection import AsyncCollection
from .collections import AsyncCollections
from .conversations_models import AsyncConversationsModels
from .curation_sets import AsyncCurationSets
from .debug import AsyncDebug
from .keys import AsyncKeys
from .metrics import AsyncMetrics
from .multi_search import AsyncMultiSearch
from .nl_search_models import AsyncNLSearchModels
from .operations import AsyncOperations
from .stemming import AsyncStemming
from .stopwords import AsyncStopwords
from .synonym_sets import AsyncSynonymSets
from typesense.configuration import ConfigDict, Configuration
from typesense.http_backend import AsyncClientType

TDoc = typing.TypeVar("TDoc", bound=DocumentSchema)


class AsyncClient:
    """
    The main client class for interacting with Typesense.

    This class serves as the entry point for all Typesense operations. It initializes
    and provides access to various components of the Typesense SDK, such as collections,
    multi-search, keys, aliases, analytics, stemming, operations, debug, stopwords,
    and conversation models.

    Attributes:
        config (Configuration): The configuration object for the Typesense client.
        api_call (ApiCall): The ApiCall instance for making API requests.
        collections (Collections[DocumentSchema]): Instance for managing collections.
        multi_search (MultiSearch): Instance for performing multi-search operations.
        keys (Keys): Instance for managing API keys.
        aliases (Aliases): Instance for managing collection aliases.
        analyticsV1 (AnalyticsV1): Instance for analytics operations (V1).
        analytics (Analytics): Instance for analytics operations (v30).
        curation_sets (CurationSets): Instance for Curation Sets (v30+)
        stemming (Stemming): Instance for stemming dictionary operations.
        operations (Operations): Instance for various Typesense operations.
        debug (Debug): Instance for debug operations.
        stopwords (Stopwords): Instance for managing stopwords.
        metrics (Metrics): Instance for retrieving system and Typesense metrics.
        conversations_models (ConversationsModels): Instance for managing conversation models.
    """

    def __init__(
        self,
        config_dict: ConfigDict,
        http_client: typing.Optional[AsyncClientType] = None,
    ) -> None:
        """
        Initialize the Client instance.

        Args:
            config_dict (ConfigDict):
                A dictionary containing the configuration for the Typesense client.

            http_client (httpx.AsyncClient | httpx2.AsyncClient, optional):
                A client to send requests with instead of the default httpx client,
                e.g. an ``httpx2.AsyncClient`` (``pip install typesense[httpx2]``).
                The connection pool and ``verify`` settings in ``config_dict`` are
                not applied to it, and the Typesense client does not close it.

        Example:
            >>> config = {
            ...     "api_key": "your_api_key",
            ...     "nodes": [
            ...         {"host": "localhost", "port": "8108", "protocol": "http"}
            ...     ],
            ...     "connection_timeout_seconds": 2,
            ... }
            >>> client = Client(config)
        """
        self.config = Configuration(config_dict)
        self.api_call = AsyncApiCall(self.config, http_client)
        self.collections: AsyncCollections[DocumentSchema] = AsyncCollections(
            self.api_call
        )
        self.multi_search = AsyncMultiSearch(self.api_call)
        self.keys = AsyncKeys(self.api_call)
        self.aliases = AsyncAliases(self.api_call)
        self._analyticsV1 = AsyncAnalyticsV1(self.api_call)
        self.analytics = AsyncAnalytics(self.api_call)
        self.stemming = AsyncStemming(self.api_call)
        self.curation_sets = AsyncCurationSets(self.api_call)
        self.operations = AsyncOperations(self.api_call)
        self.debug = AsyncDebug(self.api_call)
        self.stopwords = AsyncStopwords(self.api_call)
        self.synonym_sets = AsyncSynonymSets(self.api_call)
        self.metrics = AsyncMetrics(self.api_call)
        self.conversations_models = AsyncConversationsModels(self.api_call)
        self.nl_search_models = AsyncNLSearchModels(self.api_call)

    @property
    @deprecated(
        "AnalyticsV1 is deprecated on v30+. Use client.analytics instead.",
        category=None,
    )
    def analyticsV1(self) -> AsyncAnalyticsV1:
        return self._analyticsV1

    def typed_collection(
        self,
        *,
        model: typing.Type[TDoc],
        name: typing.Union[str, None] = None,
    ) -> AsyncCollection[TDoc]:
        """
        Get a AsyncCollection instance for a specific document model.

        This method allows retrieving a AsyncCollection instance typed to a specific document model.
        If no name is provided, it uses the lowercase name of the model class as
        the collection name.

        Args:
            model (Type[TDoc]): The document model class.
            name (Union[str, None], optional):
                The name of the collection. If None, uses the lowercase model class name.

        Returns:
            AsyncCollection[TDoc]: An AsyncCollection instance typed to the specified document model.

        Example:
            >>> class Company(DocumentSchema):
            ...     name: str
            ...     num_employees: int
            >>> client = Client(config)
            >>> companies_collection = client.typed_collection(model=Company)
            # This is equivalent to:
            # companies_collection = client.typed_collection(model=Company, name="company")
        """
        if name is None:
            name = model.__name__.lower()
        # ``collections`` is typed for the default DocumentSchema; narrow it to the model.
        return typing.cast(AsyncCollection[TDoc], self.collections[name])
