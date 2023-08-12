from _typeshed import Incomplete

logger: Incomplete
GETATTR: str
GET: str

class PathExtractionError(ValueError): ...
class RootCanNotBeModified(ValueError): ...

DEFAULT_FIRST_ELEMENT: Incomplete

def extract(obj, path): ...
