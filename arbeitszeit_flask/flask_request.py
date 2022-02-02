from typing import Optional

from flask import request


class FlaskRequest:
    def get_arg(self, arg: str) -> Optional[str]:
        return request.args.get(arg, None)

    def get_environ(self, key: str) -> Optional[str]:
        return request.environ.get(key, None)
