from deepdiff.helper import numbers as numbers, strings as strings

DEFAULT_SIGNIFICANT_DIGITS_WHEN_IGNORE_NUMERIC_TYPES: int
TYPE_STABILIZATION_MSG: str

class Base:
    numbers = numbers
    strings = strings
    def get_significant_digits(self, significant_digits, ignore_numeric_type_changes): ...
    def get_ignore_types_in_groups(self, ignore_type_in_groups, ignore_string_type_changes, ignore_numeric_type_changes, ignore_type_subclasses): ...
