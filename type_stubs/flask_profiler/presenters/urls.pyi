from typing import Dict
from urllib.parse import ParseResult as ParseResult

def get_url_with_query(route: str, url_query: Dict[str, str]) -> ParseResult: ...
