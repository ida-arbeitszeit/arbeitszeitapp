from _typeshed import Incomplete
from deepdiff.helper import OrderedSetPlus as OrderedSetPlus, RE_COMPILED_TYPE as RE_COMPILED_TYPE, add_to_frozen_set as add_to_frozen_set, dict_ as dict_, get_doc as get_doc, numbers as numbers, strings as strings

logger: Incomplete
doc: Incomplete

class DeepSearch(dict):
    warning_num: int
    obj: Incomplete
    case_sensitive: Incomplete
    exclude_paths: Incomplete
    exclude_regex_paths: Incomplete
    exclude_types: Incomplete
    exclude_types_tuple: Incomplete
    verbose_level: Incomplete
    use_regexp: Incomplete
    strict_checking: Incomplete
    match_string: Incomplete
    def __init__(self, obj, item, exclude_paths=..., exclude_regex_paths=..., exclude_types=..., verbose_level: int = ..., case_sensitive: bool = ..., match_string: bool = ..., use_regexp: bool = ..., strict_checking: bool = ..., **kwargs) -> None: ...

class grep:
    __doc__ = doc
    item: Incomplete
    kwargs: Incomplete
    def __init__(self, item, **kwargs) -> None: ...
    def __ror__(self, other): ...
