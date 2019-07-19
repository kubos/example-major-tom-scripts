
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


class UnkownObjectError(ApiError):
    """
    Raised when a query for a single item returns a null (nothing found).
    ".object" is the type of object being retrieved.
    ".id" is the ID used to retrieve it.
    ".name" is the name used to retrieve it.
    ".parent" is the parent object it should be on, "None" if it has no parent.
    """

    def __init__(self, object: str, id=None, name=None, parent=None):
        self.object = object
        self.id = id
        self.name = name
        self.parent = parent
        if id:
            message = f'No "{object}" found with id "{id}"'
        else:
            message = f'No "{object}" found with name "{name}"'
        if parent:
            message += f' under parent "{parent}"'
        super().__init__(message)
