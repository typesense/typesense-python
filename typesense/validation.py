from typesense.exceptions import InvalidParameter


def validate_search(params):
    for key in params:
        if not isinstance(params[key], str):
            raise InvalidParameter(f"'{key}' field expected a string but was given {type(params[key]).__name__}")
