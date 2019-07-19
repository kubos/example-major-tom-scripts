
class ApiError(Exception):
    """Base error class for the API"""


class QueryError(ApiError):
    """
    Raised when a query fails with an non-null "error" field.
    ".request" is the raw request
    ".errors" returns the errors field from the query
    """

    def __init__(self, request, errors):
        self.request = request
        self.server_errors = errors
        super().__init__(f"Server failed to process the query: {errors}")


class MutationError(ApiError):
    """
    Raised when a mutation "success" field returns False.
    ".request" contains the request object.
    """

    def __init__(self, request):
        self.request = request
        super().__init__(f"{request['notice']}: {request['errors']}")


class NoMatchError(ApiError):
    """
    Raised when a query for a single item returns a null (nothing matched).
    ".key" is the key used to retrieve it, such as a name or ID.
    ".parent" is the parent object it should be on, "None" if it has no parent.
    ".request" contains the raw request response.
    """

    def __init__(self, object: str, key, parent=None):
        self.object = object
        self.key = key
        self.parent = parent
        if parent != None:
            message = f'No "{object}" found with key "{key}" under parent "{parent}"'
        else:
            message = f'No "{object}" found with key "{key}"'
        super().__init__(message)
