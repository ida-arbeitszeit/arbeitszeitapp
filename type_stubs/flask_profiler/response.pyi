class HttpResponse:
    status_code: int
    content: str
    def __init__(self, status_code, content) -> None: ...
