from typesense.exceptions import InvalidParameter


def validate_search(params):
    for key in params:
        if type(params[key]) is not str:
            raise InvalidParameter(f"'{key}' field expected a string but was given {type(params[key]).__name__}")
