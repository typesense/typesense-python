class TypesenseClientError:
    pass


class Timeout(TypesenseClientError):
    pass


class RequestMalformed(TypesenseClientError):
    pass


class RequestUnauthorized(TypesenseClientError):
    pass


class ObjectNotFound(TypesenseClientError):
    pass


class ObjectAlreadyExists(TypesenseClientError):
    pass


class ObjectUnprocessable(TypesenseClientError):
    pass


class ServerError(TypesenseClientError):
    pass