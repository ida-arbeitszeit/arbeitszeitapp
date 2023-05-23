from typing import Any, Optional


class String:
    ...


class Nested:
    def __init__(self, model: Any, as_list: Optional[bool] = ...) -> None:
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


class Integer:
    ...


class List:
    def __init__(self, cls_or_instance, **kwargs):
        ...
    @property
    def container(self): ...
