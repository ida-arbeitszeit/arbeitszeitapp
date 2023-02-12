from typing import Any


class String:
    ...


class Nested:
    def __init__(self, model: Any, as_list: bool) -> None:
        ...

    @property
    def model(self):
        ...


class Arbitrary:
    ...


class Boolean:
    ...


class DateTime:
    ...
