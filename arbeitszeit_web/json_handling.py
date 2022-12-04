import json
from datetime import datetime
from decimal import Decimal
from typing import Dict
from uuid import UUID


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, UUID):
            return str(o)
        elif isinstance(o, Decimal):
            return str(o)
        elif isinstance(o, datetime):
            return datetime.isoformat(o)
        return json.JSONEncoder.default(self, o)


def dict_to_json(dictionary: Dict) -> str:
    return json.dumps(dictionary, cls=JsonEncoder)
