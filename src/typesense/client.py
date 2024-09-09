import sys

from typesense.types.document import DocumentSchema

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.collection import Collection

from .aliases import Aliases
from .analytics import Analytics
from .api_call import ApiCall
from .collections import Collections
from .configuration import ConfigDict, Configuration
from .conversations_models import ConversationsModels
from .debug import Debug
from .keys import Keys
from .multi_search import MultiSearch
from .operations import Operations
from .stopwords import Stopwords

TDoc = typing.TypeVar("TDoc", bound=DocumentSchema)


class Client(object):
    def __init__(self, config_dict: ConfigDict) -> None:
        self.config = Configuration(config_dict)
        self.api_call = ApiCall(self.config)
        self.collections: Collections[DocumentSchema] = Collections(self.api_call)
        self.multi_search = MultiSearch(self.api_call)
        self.keys = Keys(self.api_call)
        self.aliases = Aliases(self.api_call)
        self.analytics = Analytics(self.api_call)
        self.operations = Operations(self.api_call)
        self.debug = Debug(self.api_call)
        self.stopwords = Stopwords(self.api_call)
        self.conversations_models = ConversationsModels(self.api_call)

    def typed_collection(
        self,
        *,
        model: typing.Type[TDoc],
        name: typing.Union[str, None] = None,
    ) -> Collection[TDoc]:
        if name is None:
            name = model.__name__.lower()
        collection: Collection[TDoc] = self.collections[name]
        return collection
