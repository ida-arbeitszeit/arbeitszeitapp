from tests.api.namespace import ModelImpl


class NestedListFieldImpl:
    def __init__(self, model: ModelImpl, as_list: bool):
        self.model = model
        self.as_list = as_list


class StringFieldImpl:
    ...


class DateTimeFieldImpl:
    ...


class DecimalFieldImpl:
    ...


class BooleanFieldImpl:
    ...
