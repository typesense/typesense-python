"""Types for document operations in Typesense."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


_InfixOperations = typing.Literal["off", "always", "fallback"]
"""
Infix operations for search queries.

- `off`:  infix search is disabled, which is default.
- `always`: infix search is performed along with regular search.
- `fallback`: infix search is performed if regular search does not produce results.
"""

_SequenceTypes = typing.Union[
    typing.Sequence[int],
    typing.Sequence[str],
    typing.Sequence[float],
]

_Types = typing.Union[int, str, float, bool]

DocumentSchema: typing.TypeAlias = typing.Mapping[
    str,
    typing.Union[
        _Types,
        _SequenceTypes,
        "DocumentSchema",
        typing.Sequence["DocumentSchema"],
    ],
]
"""
Valid types for a document schema.

It can be a mapping of a string to any of the following types:

- `int`
- `str`
- `float`
- `bool`

Their respective sequences, or a nested schema of the same type.
"""

TDoc = typing.TypeVar("TDoc", bound="DocumentSchema")


class DirtyValuesParameters(typing.TypedDict):
    """
    Parameters for handling dirty values in documents.

    - `coerce_or_reject`: Attempt coercion of the field's value to previously inferred type.
      If coercion fails, reject the write outright with an error message.
    - `coerce_or_drop`: Attempt coercion of the field's value to previously inferred type.
      If coercion fails, drop the particular field and index the rest of the document.
    - `drop`: Drop the particular field and index the rest of the document.
    - `reject`: Reject the write outright with an error message.
    """

    dirty_values: typing.NotRequired[
        typing.Literal["coerce_or_reject", "coerce_or_drop", "drop", "reject"]
    ]


class DocumentWriteParameters(DirtyValuesParameters):
    """
    Parameters for writing documents.

    Attributes:
      action (str): [Action](https://typesense.org/docs/26.0/api/documents.html#action-modes-create-upsert-update-emplace) to perform on the document.

        - `create`: Creates a new document. Fails if a document with the same id
          already exists (default).
        - `upsert`: Creates a new document or updates an existing document if a
          document with the same id already exists. Requires the whole document to be sent.
          For partial updates, use the update action below.
        - `update`: Updates an existing document. Fails if a document with the
          given id does not exist. You can send a partial document containing only the
          fields that are to be updated.
        - `emplace`: Creates a new document or updates an existing document if a
          document with the same id already exists. You can send either the whole document
          or a partial document for update.

      dirty_values (str): [Handling of dirty values](https://typesense.org/docs/26.0/api/documents.html#dealing-with-dirty-data) in the document.

        - `coerce_or_reject`: Attempt coercion of the field's value to previously inferred type.
          If coercion fails, reject the write outright with an error message.
        - `coerce_or_drop`: Attempt coercion of the field's value to previously inferred type.
          If coercion fails, drop the particular field and index the rest of the document.
        - `drop`: Drop the particular field and index the rest of the document.
        - `reject`: Reject the write outright with an error message.
    """

    action: typing.NotRequired[typing.Literal["create", "update", "upsert", "emplace"]]


class UpdateByFilterParameters(typing.TypedDict):
    """
    Parameters for updating documents by filter.

    Attributes:
      filter_by(str): Filter to apply to documents.
    """

    filter_by: str


class UpdateByFilterResponse(typing.TypedDict):
    """
    Response from updating documents by filter.

    Attributes:
      num_updated(int): Indicates the success of the operation.
    """

    num_updated: int


class ImportResponseSuccess(typing.TypedDict):
    """
    Response for a successful import operation.

    Attributes:
      success(True): Indicates the success of the operation.
    """

    success: typing.Literal[True]


class ImportResponseWithDocAndId(typing.Generic[TDoc], ImportResponseSuccess):
    """
    Response for a successful import operation with document and id.

    Attributes:
      success(True): Indicates the success of the operation.
      doc(TDoc): Imported document.
      id(str): ID of the imported document.
    """

    id: str
    doc: TDoc


class ImportResponseWithDoc(typing.Generic[TDoc], ImportResponseSuccess):
    """
    Response for a successful import operation with document.

    Attributes:
      success(True): Indicates the success of the operation.
      doc(TDoc): Imported document.
    """

    doc: TDoc


class ImportResponseWithId(ImportResponseSuccess):
    """
    Response for a successful import operation with ID.

    Attributes:
      success(True): Indicates the success of the operation.
      id(str): ID of the imported document.
    """

    id: str


class ImportResponseFail(typing.Generic[TDoc], typing.TypedDict):
    """
    Response for a failed import operation.

    Attributes:
      success (False): Indicates the success of the operation.
      error (str): Error message.
      code (int): Error code.
      document (TDoc): Document that failed to import.
    """

    success: typing.Literal[False]
    error: str
    code: int
    document: TDoc


ImportResponse: typing.TypeAlias = typing.Union[
    typing.List[typing.Union[ImportResponseWithDoc[TDoc], ImportResponseFail[TDoc]]],
    typing.List[typing.Union[ImportResponseWithId, ImportResponseFail[TDoc]]],
    typing.List[
        typing.Union[ImportResponseWithDocAndId[TDoc], ImportResponseFail[TDoc]]
    ],
    typing.List[typing.Union[ImportResponseSuccess, ImportResponseFail[TDoc]]],
]
"""Set of all possible responses after an import operation."""


class DocumentImportParametersReturnId(DocumentWriteParameters):
    """
    Parameters for importing documents with return ID.

    Attributes:
      return_id (True): Return the ID of the imported document.
      action (str): [Action](https://typesense.org/docs/26.0/api/documents.html#action-modes-create-upsert-update-emplace) to perform on the document.

        - `create`: Creates a new document. Fails if a document with the same id
          already exists (default).
        - `upsert`: Creates a new document or updates an existing document if a
          document with the same id already exists. Requires the whole document to be sent.
          For partial updates, use the update action below.
        - `update`: Updates an existing document. Fails if a document with the
          given id does not exist. You can send a partial document containing only the
          fields that are to be updated.
        - `emplace`: Creates a new document or updates an existing document if a
          document with the same id already exists. You can send either the whole document
          or a partial document for update.

      dirty_values (str): [Handling of dirty values](https://typesense.org/docs/26.0/api/documents.html#dealing-with-dirty-data) in the document.

        - `coerce_or_reject`: Attempt coercion of the field's value to previously inferred type.
          If coercion fails, reject the write outright with an error message.
        - `coerce_or_drop`: Attempt coercion of the field's value to previously inferred type.
          If coercion fails, drop the particular field and index the rest of the document.
        - `drop`: Drop the particular field and index the rest of the document.
        - `reject`: Reject the write outright with an error message.
    """

    return_id: typing.Literal[True]


class DocumentImportParametersReturnDoc(DocumentWriteParameters):
    """
    Parameters for importing documents with return document.

    Attributes:
      return_doc (True): Return the imported document.
      action (str): [Action](https://typesense.org/docs/26.0/api/documents.html#action-modes-create-upsert-update-emplace) to perform on the document.

        - `create`: Creates a new document. Fails if a document with the same id
          already exists (default).
        - `upsert`: Creates a new document or updates an existing document if a
          document with the same id already exists. Requires the whole document to be sent.
          For partial updates, use the update action below.
        - `update`: Updates an existing document. Fails if a document with the
          given id does not exist. You can send a partial document containing only the
          fields that are to be updated.
        - `emplace`: Creates a new document or updates an existing document if a
          document with the same id already exists. You can send either the whole document
          or a partial document for update.

      dirty_values (str): [Handling of dirty values](https://typesense.org/docs/26.0/api/documents.html#dealing-with-dirty-data) in the document.

        - `coerce_or_reject`: Attempt coercion of the field's value to previously inferred type.
          If coercion fails, reject the write outright with an error message.
        - `coerce_or_drop`: Attempt coercion of the field's value to previously inferred type.
          If coercion fails, drop the particular field and index the rest of the document.
        - `drop`: Drop the particular field and index the rest of the document.
        - `reject`: Reject the write outright with an error message.
    """

    return_doc: typing.Literal[True]


class DocumentImportParametersReturnDocAndId(DocumentWriteParameters):
    """
    Parameters for importing documents with return document and ID.

    Attributes:
      return_doc (True): Return the imported document.
      return_id (True): Return the ID of the imported document.
      action (str): [Action](https://typesense.org/docs/26.0/api/documents.html#action-modes-create-upsert-update-emplace) to perform on the document.

        - `create`: Creates a new document. Fails if a document with the same id
          already exists (default).
        - `upsert`: Creates a new document or updates an existing document if a
          document with the same id already exists. Requires the whole document to be sent.
          For partial updates, use the update action below.
        - `update`: Updates an existing document. Fails if a document with the
          given id does not exist. You can send a partial document containing only the
          fields that are to be updated.
        - `emplace`: Creates a new document or updates an existing document if a
          document with the same id already exists. You can send either the whole document
          or a partial document for update.

      dirty_values (str): [Handling of dirty values](https://typesense.org/docs/26.0/api/documents.html#dealing-with-dirty-data) in the document.

        - `coerce_or_reject`: Attempt coercion of the field's value to previously inferred type.
          If coercion fails, reject the write outright with an error message.
        - `coerce_or_drop`: Attempt coercion of the field's value to previously inferred type.
          If coercion fails, drop the particular field and index the rest of the document.
        - `drop`: Drop the particular field and index the rest of the document.
        - `reject`: Reject the write outright with an error message.
    """

    return_doc: typing.Literal[True]
    return_id: typing.Literal[True]


DocumentImportParameters: typing.TypeAlias = typing.Union[
    DocumentWriteParameters,
    DocumentImportParametersReturnId,
    DocumentImportParametersReturnDoc,
    DocumentImportParametersReturnDocAndId,
]
"""Set of all possible parameters for importing documents."""


class DocumentExportParameters(typing.TypedDict):
    """
    Parameters for [exporting documents](https://typesense.org/docs/26.0/api/documents.html#export-documents).

    Attributes:
      filter_by (str): Filter to apply to documents.
      include_fields (str): Fields to include in the exported documents.
      exclude_fields (str): Fields to exclude from the exported documents.
    """

    filter_by: typing.NotRequired[str]
    include_fields: typing.NotRequired[str]
    exclude_fields: typing.NotRequired[str]


class RequiredSearchParameters(typing.TypedDict):
    """
    Required parameters for searching documents.

    Attributes:
      q (str): Query string to search for.
      query_by (str): Field to search in.
    """

    q: str
    query_by: str


class QueryParameters(typing.TypedDict):
    """
    Parameters [regarding queries](https://typesense.org/docs/26.0/api/search.html#query-parameters).

    Attributes:
      prefix (str, bool, list[bool]): Prefix operations for search queries.
      infix (InfixOperations, list[InfixOperations]): Infix operations for search queries.
      pre_segmented_query (bool): Indicates whether the query is pre-segmented.
      preset (str): Preset for search queries.
      vector_query (str): Vector query for search.
      voice_query (str): Voice query for search.
      stopwords (str, list[str]): A comma separated list of words to be dropped from the search query while searching.
      validate_field_names (bool): Controls whether Typesense should validate if the fields exist in the schema.
    """

    prefix: typing.NotRequired[typing.Union[str, bool, typing.List[bool]]]
    infix: typing.NotRequired[
        typing.Union[_InfixOperations, typing.List[_InfixOperations]]
    ]
    pre_segmented_query: typing.NotRequired[bool]
    preset: typing.NotRequired[str]
    vector_query: typing.NotRequired[str]
    voice_query: typing.NotRequired[str]
    stopwords: typing.NotRequired[typing.Union[str, typing.List[str]]]
    validate_field_names: typing.NotRequired[bool]


class FilterParameters(typing.TypedDict):
    """
    Parameters regarding [filtering search responses](https://typesense.org/docs/26.0/api/search.html#filter-parameters).

    Attributes:
      filter_by (str): Filter to apply to search results.
      enable_lazy_filter (bool): Enable lazy filtering.
    """

    filter_by: typing.NotRequired[str]
    max_filter_by_candidates: typing.NotRequired[int]
    enable_lazy_filter: typing.NotRequired[bool]


class RankingAndSortingParameters(typing.TypedDict):
    """
    Parameters regarding [ranking and sorting search results](https://typesense.org/docs/26.0/api/search.html#ranking-and-sorting-parameters).

    Attributes:
      query_by_weights (str, list[int]): Weights to apply to query fields.
      text_match_type (str): Type of text match to prioritize.

        - `max_score`: Prioritize maximum score.
        - `max_weight`: Prioritize maximum weight.

      sort_by (str, list[str]): Fields to sort search results by in order specified.
      prioritize_exact_match (bool): Prioritize exact matches.
      prioritize_token_position (bool): Prioritize token position.
      prioritize_num_matching_fields (bool): Prioritize number of matching fields.
      pinned_hits (dict[str, list[str]]): Pinned hits to prioritize.
      hidden_hits (dict[str, list[str]]): Hidden hits to deprioritize.
      enable_overrides (bool): Enable overrides.
      override_tags (str, list[str]): Tags to override.
      max_candidates (int): Maximum number of candidates to return.
      enable_synonyms (bool): If you have some synonyms defined but want to disable all of them for a particular search query, set `enable_synonyms` to `false`.
      filter_curated_hits (bool): Whether the `filter_by` condition of the search query should be applicable to curated results (override definitions, pinned hits, hidden hits, etc.
      synonym_prefix (bool): Allow synonym resolution on word prefixes in the query.
    """

    query_by_weights: typing.NotRequired[typing.Union[str, typing.List[int]]]
    text_match_type: typing.NotRequired[typing.Literal["max_score", "max_weight"]]
    sort_by: typing.NotRequired[typing.Union[str, typing.List[str]]]
    prioritize_exact_match: typing.NotRequired[bool]
    prioritize_token_position: typing.NotRequired[bool]
    prioritize_num_matching_fields: typing.NotRequired[bool]
    pinned_hits: typing.NotRequired[typing.Dict[str, typing.List[str]]]
    hidden_hits: typing.NotRequired[typing.Dict[str, typing.List[str]]]
    enable_overrides: typing.NotRequired[bool]
    override_tags: typing.NotRequired[typing.Union[str, typing.List[str]]]
    max_candidates: typing.NotRequired[int]
    enable_synonyms: typing.NotRequired[bool]
    filter_curated_hits: typing.NotRequired[bool]
    synonym_prefix: typing.NotRequired[bool]


class PaginationParameters(typing.TypedDict):
    """
    Parameters regarding [pagination of search results](https://typesense.org/docs/26.0/api/search.html#pagination-parameters).

    Attributes:
      page (int): Page number to retrieve.
      per_page (int): Number of results per page.
      offset (int): Offset to start retrieving results from.
      limit (int): Limit of results to retrieve.
    """

    page: typing.NotRequired[int]
    per_page: typing.NotRequired[int]
    offset: typing.NotRequired[int]
    limit: typing.NotRequired[int]


class FacetingParameters(typing.TypedDict):
    """
    Parameters regarding [faceting search results](https://typesense.org/docs/26.0/api/search.html#faceting-parameters).

    Attributes:
      facet_by (str, list[str]): Field to facet by.
      max_facet_values (int): Maximum number of facet values to return.
      facet_query (str): Query to facet by.
      facet_query_num_typos (int): Number of typos to allow in facet query.
      facet_return_parent (str): Return parent of facet.
      facet_sample_percent (int): Sample percentage of facet values to return.
      facet_sample_threshold (int): Sample threshold of facet values to return.
      facet_strategy (str): Typesense supports two strategies for efficient faceting, and has some built-in heuristics to pick the right strategy for you.
    """

    facet_by: typing.NotRequired[typing.Union[str, typing.List[str]]]
    max_facet_values: typing.NotRequired[int]
    facet_query: typing.NotRequired[str]
    facet_query_num_typos: typing.NotRequired[int]
    facet_return_parent: typing.NotRequired[str]
    facet_sample_percent: typing.NotRequired[int]
    facet_sample_threshold: typing.NotRequired[int]
    facet_strategy: typing.NotRequired[
        typing.Union[
            typing.Literal["exhaustive"],
            typing.Literal["top_values"],
            typing.Literal["automatic"],  # default
        ]
    ]


class GroupingParameters(typing.TypedDict):
    """
    Parameters regarding [grouping search results](https://typesense.org/docs/26.0/api/search.html#grouping-parameters).

    Attributes:
      group_by (str): Field to group by.
      group_limit (int): Limit of groups to return.
      group_missing_values (bool): Include missing values in groups.
    """

    group_by: typing.NotRequired[str]
    group_limit: typing.NotRequired[int]
    group_missing_values: typing.NotRequired[bool]


class ResultsParameters(typing.TypedDict):
    """
    Parameters regarding [search results](https://typesense.org/docs/26.0/api/search.html#results-parameters).

    Attributes:
      include_fields (str, list[str]): Fields to include in search results.
      exclude_fields (str, list[str]): Fields to exclude from search results.
      highlight_fields (str, list[str]): Fields to highlight in search results.
      highlight_full_fields (str, list[str]): Fields to highlight fully in search results.
      highlight_affix_num_tokens (int): The number of tokens that should surround the highlighted text on each side.
      highlight_start_tag (str): Start tag for highlighting.
      highlight_end_tag (str): End tag for highlighting.
      enable_highlight_v1 (bool): Flag for disabling the deprecated, old highlight structure in the response.
      snippet_threshold (int): Field values under this length will be fully highlighted, instead of showing a snippet of relevant portion.
      limit_hits (int): Limit the number of hits to return.
      search_cutoff_ms (int): Search cutoff time in milliseconds.
      exhaustive_search (bool): Perform exhaustive search.
    """

    include_fields: typing.NotRequired[typing.Union[str, typing.List[str]]]
    exclude_fields: typing.NotRequired[typing.Union[str, typing.List[str]]]
    highlight_fields: typing.NotRequired[
        typing.Union[typing.Literal["none"], str, typing.List[str]]
    ]
    highlight_full_fields: typing.NotRequired[
        typing.Union[typing.Literal["none"], str, typing.List[str]]
    ]
    highlight_affix_num_tokens: typing.NotRequired[int]
    highlight_start_tag: typing.NotRequired[str]
    highlight_end_tag: typing.NotRequired[str]
    enable_highlight_v1: typing.NotRequired[bool]
    snippet_threshold: typing.NotRequired[int]
    limit_hits: typing.NotRequired[int]
    search_cutoff_ms: typing.NotRequired[int]
    exhaustive_search: typing.NotRequired[bool]


class TypoToleranceParameters(typing.TypedDict):
    """
    Parameters regarding [typo tolerance in search results](https://typesense.org/docs/26.0/api/search.html#typo-tolerance-parameters).

    Attributes:
      num_typos (int): Number of typos to allow in search results.
      min_len_1typo (int): Minimum length of query to allow one typo.
      min_len_2typo (int): Minimum length of query to allow two typos.
      split_join_tokens (str): Treat space as a typo.
      typo_tokens_threshold (int): Threshold for typo tokens.
      drop_tokens_threshold (int): Threshold for dropping tokens.
      drop_tokens_mode (str): Mode for dropping tokens.


        - `right_to_left`: Drop tokens from right to left (default).
        - `left_to_right`: Drop tokens from left to right.
        - `both_sides:3`: Drop tokens from both sides with a threshold of 3.
          Afterwards, drops back to the default right to left.

      enable_typos_for_numerical_tokens (bool): Set this parameter to `false` to disable typos on numerical query tokens.
      enable_typos_for_alpha_numerical_tokens (bool): Set this parameter to `false` to disable typos on alphanumerical query tokens.
      synonym_num_typos (int): Allow synonym resolution on typo-corrected words in the query.
    """

    num_typos: typing.NotRequired[int]
    min_len_1typo: typing.NotRequired[int]
    min_len_2typo: typing.NotRequired[int]
    split_join_tokens: typing.NotRequired[typing.Literal["off", "fallback", "always"]]
    typo_tokens_threshold: typing.NotRequired[int]
    drop_tokens_threshold: typing.NotRequired[int]
    drop_tokens_mode: typing.NotRequired[
        typing.Literal["right_to_left", "left_to_right", "both_sides:3"]
    ]
    enable_typos_for_numerical_tokens: typing.NotRequired[bool]
    enable_typos_for_alpha_numerical_tokens: typing.NotRequired[bool]
    synonym_num_typos: typing.NotRequired[int]


class CachingParameters(typing.TypedDict):
    """
    Parameters regarding [caching search results](https://typesense.org/docs/26.0/api/search.html#caching-parameters).

    Attributes:
      use_cache (bool): Use cache for search results.
      cache_ttl (int): The duration (in seconds) that determines how long the search query is cached.
    """

    use_cache: typing.NotRequired[bool]
    cache_ttl: typing.NotRequired[int]


class SearchParameters(
    RequiredSearchParameters,
    QueryParameters,
    FilterParameters,
    RankingAndSortingParameters,
    PaginationParameters,
    FacetingParameters,
    GroupingParameters,
    ResultsParameters,
    TypoToleranceParameters,
    CachingParameters,
):
    """Parameters for searching documents."""


class MultiSearchParameters(SearchParameters):
    """
    Parameters for performing a [Federated/Multi-Search](https://typesense.org/docs/26.0/api/federated-multi-search.html#federated-multi-search).

    Attributes:
        collection (str): Collection to search in.

    Plus all the parameters from `SearchParameters`.
    """

    collection: str
    rerank_hybrid_matches: typing.NotRequired[bool]


class MultiSearchCommonParameters(
    QueryParameters,
    FilterParameters,
    RankingAndSortingParameters,
    PaginationParameters,
    FacetingParameters,
    GroupingParameters,
    ResultsParameters,
    TypoToleranceParameters,
    CachingParameters,
):
    """
    [Query parameters](https://typesense.org/docs/26.0/api/federated-multi-search.html#multi-search-parameters) for multi-search.

    Attributes:
        query_by (str): Field to search in.
        limit_multi_searches (int): Limit the number of multi-searches.
        x_typesense_api_key (str): API key for Typesense.

    You can also use any of the parameters from `SearchParameters`.
    """

    query_by: typing.NotRequired[str]
    limit_multi_searches: typing.NotRequired[int]
    x_typesense_api_key: typing.NotRequired[str]


class GenerateScopedSearchKeyParams(
    QueryParameters,
    FilterParameters,
    RankingAndSortingParameters,
    PaginationParameters,
    FacetingParameters,
    GroupingParameters,
    ResultsParameters,
    TypoToleranceParameters,
    CachingParameters,
):
    """
    Parameters for generating a [scoped search key](https://typesense.org/docs/26.0/api/api-keys.html#generate-scoped-search-key).

    Attributes:
      q (str): Query string to search for.
      query_by (str): Field to search in.
      filter_by (str): Filter to apply to search results.
      expires_at (int): Expiry time (in UNIX timestamp format) for the scoped search key.
      limit_multi_searches (int): Limit the number of multi-searches.

    You can also embed any of the parameters from `SearchParameters`.
    """

    q: typing.NotRequired[str]
    query_by: typing.NotRequired[str]
    expires_at: typing.NotRequired[int]
    limit_multi_searches: typing.NotRequired[int]


class FacetCountSchema(typing.TypedDict):
    """
    Schema for facet count.

    Attributes:
      count (int): Number of occurrences of the facet value.
      value (str): Value of the facet.
      highlighted (str): Highlighted value of the facet.
    """

    count: int
    value: str
    highlighted: str


class FacetCountStats(typing.TypedDict):
    """
    Statistics for facet count.

    Attributes:
      min (float): Minimum value of the facet.
      max (float): Maximum value of the facet.
      avg (float): Average value of the facet.
      sum (float): Sum of the facet values.
      total_values (int): Total number of values.
    """

    min: typing.NotRequired[float]
    max: typing.NotRequired[float]
    avg: typing.NotRequired[float]
    sum: typing.NotRequired[float]
    total_values: typing.NotRequired[int]


class SearchResponseFacetCountSchema(typing.TypedDict):
    """
    Schema for the search response facet count.

    Attributes:
      counts (list[FacetCountSchema]): List of facet counts.
      field_name (str): Name of the field.
      stats (FacetCountStats): Statistics for the facet count.
    """

    counts: typing.List[FacetCountSchema]
    field_name: str
    stats: FacetCountStats


class Highlight(typing.TypedDict):
    """
    Schema for highlighting search results.

    Attributes:
      matched_tokens (list[str]): List of matched tokens.
      snippet (str): Snippet of the matched tokens.
      value (str): Value of the matched tokens.
    """

    matched_tokens: typing.List[str]
    snippet: str
    value: str


class HighlightExtended(Highlight):
    """
    Extended schema for highlighting search results.

    Attributes:
      field (str): Field to highlight.

    Plus all the parameters from `Highlight`.
    """

    field: str


class TextMatchInfo(typing.TypedDict):
    """
    Schema for text match information.

    Attributes:
      best_field_score (str): Best field score.
      best_field_weight (int): Best field weight.
      fields_matched (int): Number of fields matched.
      score (str): Score of the text match.
      typo_prefix_score (int): Typo prefix score.
      num_tokens_dropped (int): Number of tokens dropped.
      tokens_matched (int): Number of tokens matched.
    """

    best_field_score: str
    best_field_weight: int
    fields_matched: int
    score: str
    typo_prefix_score: int
    num_tokens_dropped: int
    tokens_matched: int


class Hit(typing.Generic[TDoc], typing.TypedDict):
    """
    Schema for a hit in search results.

    Attributes:
      document (TDoc): Document in the hit.
      highlights (list[HighlightExtended]): List of highlights in the hit.
      highlight (dict[str, Highlight]): Dictionary of highlights in the hit.
      text_match (int): Text match in the hit.
      text_match_info (TextMatchInfo): Text match information in the hit.
    """

    document: TDoc
    highlights: typing.List[HighlightExtended]
    highlight: typing.Dict[str, Highlight]
    text_match: int
    text_match_info: TextMatchInfo


class GroupedHit(typing.Generic[TDoc], typing.TypedDict):
    """
    Schema for grouped hits in search results.

    Attributes:
      group_key (list[str]): List of group keys.
      hits (list[Hit[TDoc]]): List of hits in the group.
      found (int): Number of hits found.
    """

    group_key: typing.List[str]
    hits: typing.List[Hit[TDoc]]
    found: typing.NotRequired[int]


class ConversationHistory(typing.TypedDict):
    """
    Schema for a conversation's history in the search results.

    Attributes:
      conversation (list[object]): List of conversation objects.
      id (str): ID of the conversation.
      last_updated (int): Last updated time of the conversation.
      ttl (int): Time to live of the conversation.
    """

    conversation: typing.List[object]
    id: str
    last_updated: int
    ttl: int


class Conversation(typing.TypedDict):
    """
    Schema for a conversation in the search results.

    Attributes:
      answer (str): Answer to the query.
      conversation_history (ConversationHistory): Conversation history.
      conversation_id (str): ID of the conversation.
      query (str): Query of the conversation.
    """

    answer: str
    conversation_history: ConversationHistory
    conversation_id: str
    query: str


class SearchResponse(typing.Generic[TDoc], typing.TypedDict):
    """
    Schema for a search response.

    Attributes:
      facet_counts (list[SearchResponseFacetCountSchema]): List of facet counts.
      found (int): Number of documents found.
      found_docs (int): Number of documents found.
      page (int): Page number of the search results.
      out_of (int): Number of documents found out of the whole dataset.
      search_time_ms (int): Search time in milliseconds.
      search_cutoff (bool): Search cutoff.
      hits (list[Hit[TDoc]]): List of hits in the search results.
      grouped_hits (list[GroupedHit[TDoc]]): List of grouped hits in the search results.
      conversation (Conversation): Conversation in the search results.
    """

    facet_counts: typing.List[SearchResponseFacetCountSchema]
    found: int
    found_docs: typing.NotRequired[int]
    page: int
    out_of: int
    search_time_ms: int
    search_cutoff: typing.NotRequired[bool]
    hits: typing.List[Hit[TDoc]]
    grouped_hits: typing.NotRequired[typing.List[GroupedHit[TDoc]]]
    conversation: typing.NotRequired[Conversation]


class DeleteSingleDocumentParameters(typing.TypedDict):
    """
    Parameters for deleting a single document.

    Attributes:
      ignore_not_found (bool): Ignore not found documents.
    """

    ignore_not_found: typing.NotRequired[bool]


class DeleteQueryParameters(typing.TypedDict):
    """
    Parameters for deleting documents.

    Attributes:
      truncate (str): Truncate the collection, keeping just the schema.
      filter_by (str): Filter to apply to documents.
      batch_size (int): Batch size for deleting documents.
      ignore_not_found (bool): Ignore not found documents.
    """

    truncate: typing.NotRequired[bool]
    filter_by: str
    batch_size: typing.NotRequired[int]
    ignore_not_found: typing.NotRequired[bool]


class DeleteResponse(typing.TypedDict):
    """
    Response from deleting documents.

    Attributes:
      num_deleted (int): Number of documents deleted.
    """

    num_deleted: int


class RetrieveParameters(typing.TypedDict):
    """
    Parameters for retrieving documents.

    Attributes:
      include_fields (str): Fields to include in the retrieved documents.
      exclude_fields (str): Fields to exclude from the retrieved documents.
    """

    include_fields: typing.NotRequired[typing.Union[str, typing.List[str]]]
    exclude_fields: typing.NotRequired[typing.Union[str, typing.List[str]]]
