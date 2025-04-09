"""Collection types for Typesense Python Client."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


_TType = typing.TypeVar("_TType")

_FieldType = typing.Literal[
    "string",
    "int32",
    "int64",
    "float",
    "bool",
    "geopoint",
    "geopolygon",
    "geopoint[]",
    "string[]",
    "int32[]",
    "int64[]",
    "float[]",
    "bool[]",
    "object",
    "object[]",
    "auto",
    "string*",
    "image",
]

_ReferenceFieldType = typing.Literal["string", "int32", "int64", "float"]

Locales = typing.Literal["ja", "zh", "ko", "th", "el", "ru", "rs", "uk", "be", ""]


class HNSWParamsSchema(typing.TypedDict):
    """
    The schema for the HNSW parameters in the CollectionFieldSchema.

    Attributes:
        M (int): The number of bi-directional links created for every new element.
        ef_construction (int): The size of the dynamic list for the nearest neighbors.
    """

    M: typing.NotRequired[int]
    ef_construction: typing.NotRequired[int]


class CollectionFieldSchema(typing.Generic[_TType], typing.TypedDict, total=False):
    """
    CollectionFieldSchema represents the schema of a field in a collection.

    Attributes:
      name (str): The name of the field.
      type (TType): The type of the field.
      facet (bool): Whether the field is a facet.
      optional (bool): Whether the field is optional.
      infix (bool): Whether the field is an infix.
      stem (bool): Whether the field is a stem.
      symbols_to_index (list[str]): The symbols to index
      token_separators (list[str]): The token separators.
      locale (Locales): The locale of the field.
      sort (bool): Whether the field is sortable.
      store (bool): Whether the field is stored.
      num_dim (float): The number of dimensions.
      range_index (bool): Whether the field is a range index.
      index (bool): Whether the field is indexed.
      vec_dist (typing.Literal['cosine', 'ip'] | str): The vector distance.
    """

    name: str
    type: typing.NotRequired[_TType]
    facet: typing.NotRequired[bool]
    optional: typing.NotRequired[bool]
    infix: typing.NotRequired[bool]
    stem: typing.NotRequired[bool]
    locale: typing.NotRequired[Locales]
    sort: typing.NotRequired[bool]
    store: typing.NotRequired[bool]
    symbols_to_index: typing.NotRequired[typing.List[str]]
    token_separators: typing.NotRequired[typing.List[str]]
    num_dim: typing.NotRequired[float]
    hnsw_params: typing.NotRequired[HNSWParamsSchema]
    range_index: typing.NotRequired[bool]
    index: typing.NotRequired[bool]
    vec_dist: typing.NotRequired[typing.Union[typing.Literal["cosine", "ip"], str]]


class RegularCollectionFieldSchema(CollectionFieldSchema[_FieldType]):
    """
    The schema of a regular field in a collection.

    Attributes:
      name (str): The name of the field.
      type (FieldType): The type of the field.
      facet (bool): Whether the field is a facet.
      optional (bool): Whether the field is optional.
      infix (bool): Whether the field is an infix.
      stem (bool): Whether the field is a stem.
      locale (Locales): The locale of the field.
      sort (bool): Whether the field is sortable.
      symbols_to_index (list[str]): The symbols to index
      token_separators (list[str]): The token separators.
      store (bool): Whether the field is stored.
      num_dim (float): The number of dimensions.
      range_index (bool): Whether the field is a range index.
      index (bool): Whether the field is indexed.
      vec_dist (typing.Literal['cosine', 'ip'] | str): The vector distance.
    """


class ReferenceCollectionFieldSchema(CollectionFieldSchema[_ReferenceFieldType]):
    """
    The schema of a field referencing another field from a foreign Collection.

    Attributes:
      name (str): The name of the field.
      type (ReferenceFieldType): The type of the field.
      facet (bool): Whether the field is a facet.
      optional (bool): Whether the field is optional.
      infix (bool): Whether the field is an infix.
      symbols_to_index (list[str]): The symbols to index
      token_separators (list[str]): The token separators.
      stem (bool): Whether the field is a stem.
      locale (Locales): The locale of the field.
      sort (bool): Whether the field is sortable.
      store (bool): Whether the field is stored.
      num_dim (float): The number of dimensions.
      range_index (bool): Whether the field is a range index.
      index (bool): Whether the field is indexed.
      vec_dist (typing.Literal['cosine', 'ip'] | str): The vector distance.:w
    """

    reference: str


class DropCollectionFieldSchema(typing.TypedDict):
    """The schema for the field in the CollectionUpdateSchema."""

    drop: typing.Literal[True]
    name: str


class VoiceQueryModelSchema(typing.TypedDict):
    """The schema for the voice_query_model field in the CollectionCreateSchema."""

    model_name: str


class CollectionCreateSchema(typing.TypedDict):
    """
    The schema for the request of the Collections.create method.

    Attributes:
        name (str): The name of the collection.

        fields (list[RegularCollectionFieldSchema | ReferenceCollectionFieldSchema]): The fields
            of the collection.

        default_sorting_field (str): The default sorting field of the collection.

        symbols_to_index (list[str]): The symbols to index.

        token_separators (list[str]): The token separators.

        enable_nested_fields (bool): Whether nested fields are enabled.

        voice_query_model (VoiceQueryModelSchema): The voice query model.
    """

    name: str
    fields: typing.List[
        typing.Union[RegularCollectionFieldSchema, ReferenceCollectionFieldSchema]
    ]
    default_sorting_field: typing.NotRequired[str]
    symbols_to_index: typing.NotRequired[typing.List[str]]
    token_separators: typing.NotRequired[typing.List[str]]
    enable_nested_fields: typing.NotRequired[bool]
    voice_query_model: typing.NotRequired[VoiceQueryModelSchema]


class CollectionSchema(CollectionCreateSchema):
    """
    The schema for the response of the Collections.create method.

    Attributes:
        created_at (int): The creation timestamp of the collection.

        num_documents (int): The number of documents in the collection.

        num_memory_shards (int): The number of memory shards in the collection.

        name (str): The name of the collection.

        fields (list[RegularCollectionFieldSchema | ReferenceCollectionFieldSchema]): The fields
            of the collection.

        default_sorting_field (str): The default sorting field of the collection.

        symbols_to_index (list[str]): The symbols to index.

        token_separators (list[str]): The token separators.

        enable_nested_fields (bool): Whether nested fields are enabled.

        voice_query_model (VoiceQueryModelSchema): The voice query model.
    """

    created_at: int
    num_documents: int
    num_memory_shards: int


class CollectionUpdateSchema(typing.TypedDict):
    """
    The schema for the request of the Collection.update method.

    Attributes:
        fields (list): The fields of the collection.

    """

    fields: typing.List[
        typing.Union[
            RegularCollectionFieldSchema,
            ReferenceCollectionFieldSchema,
            DropCollectionFieldSchema,
        ]
    ]
