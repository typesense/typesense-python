from typesense.exceptions import InvalidParameter


def validate_query_by(params):
    if "query_by" in params and type(params["query_by"]) is not str:
        raise InvalidParameter(f"'query_by' field expected a string but was given {type(params['query_by']).__name__}")
