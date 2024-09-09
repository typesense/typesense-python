"""
This module defines custom exception classes for the Typesense client.

Classes:
    - TypesenseClientError: Base exception class for Typesense client errors.
    - ConfigError: Raised when there is an error in the client configuration.
    - Timeout: Raised when a request times out.
    - RequestMalformed: Raised when a request's parameters are malformed.
    - RequestUnauthorized: Raised when a request is unauthorized.
    - RequestForbidden: Raised when a request is forbidden.
    - ObjectNotFound: Raised when a resource is not found.
    - ObjectAlreadyExists: Raised when a resource already exists.
    - ObjectUnprocessable: Raised when a resource is unprocessable.
    - ServerError: Raised when the server encounters an error.
    - ServiceUnavailable: Raised when the service is unavailable.
    - HTTPStatus0Error: Raised when the HTTP status code is 0.
    - InvalidParameter: Raised when a parameter is invalid.

These exception classes provide specific error types for various scenarios
that may occur when interacting with the Typesense API.

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""


class TypesenseClientError(IOError):
    """
    Base exception class for Typesense client errors.

    This class extends IOError and serves as the parent class for all
    custom Typesense client exceptions.
    """


class ConfigError(TypesenseClientError):
    """Raised when there is an error in the client configuration."""


class Timeout(TypesenseClientError):
    """Raised when a request times out."""


class RequestMalformed(TypesenseClientError):
    """Raised when a request's parameters are malformed."""


class RequestUnauthorized(TypesenseClientError):
    """Raised when a request is unauthorized."""


class RequestForbidden(TypesenseClientError):
    """Raised when a request is forbidden."""


class ObjectNotFound(TypesenseClientError):
    """Raised when a resource is not found."""


class ObjectAlreadyExists(TypesenseClientError):
    """Raised when a resource already exists."""


class ObjectUnprocessable(TypesenseClientError):
    """Raised when a resource is unprocessable."""


class ServerError(TypesenseClientError):
    """Raised when the server encounters an error."""


class ServiceUnavailable(TypesenseClientError):
    """Raised when the service is unavailable."""


class HTTPStatus0Error(TypesenseClientError):
    """Raised when the HTTP status code is 0."""


class InvalidParameter(TypesenseClientError):
    """Raised when a parameter is invalid."""
