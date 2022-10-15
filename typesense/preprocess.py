def stringify_search_params(params):
    return {key:stringify(val) for key, val in params.items()}

def stringify(val):
    if isinstance(val, bool) or isinstance(val, int):
        return str(val).lower()
    else:
        return val