from typing import Any, Optional


class String:
    def __init__(self, required: bool = ...):
        pass

    @property
    def required(self):
        ...


class Nested:
    def __init__(
        self, model: Any, as_list: Optional[bool] = ..., skip_none: bool = ...
    ) -> None:
        ...

    @property
    def model(self):
        ...


class Arbitrary:
    def __init__(self, required: bool = ...):
        pass

    @property
    def required(self):
        ...


class Boolean:
    def __init__(self, required: bool = ...):
        pass

    @property
    def required(self):
        ...


class DateTime:
    def __init__(self, required: bool = ...):
        pass

    @property
    def required(self):
        ...


class Integer:
    def __init__(self, required: bool = ...):
        pass

    @property
    def required(self):
        ...


class List:
    def __init__(self, cls_or_instance, **kwargs):
        ...

    @property
    def container(self):
        ...

    @property
    def required(self):
        ...
