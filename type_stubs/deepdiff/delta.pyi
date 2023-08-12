from _typeshed import Incomplete
from deepdiff import DeepDiff as DeepDiff
from deepdiff.anyset import AnySet as AnySet
from deepdiff.helper import dict_ as dict_, get_doc as get_doc, not_found as not_found, np_array_factory as np_array_factory, np_ndarray as np_ndarray, numbers as numbers, numpy_dtype_string_to_type as numpy_dtype_string_to_type, numpy_dtypes as numpy_dtypes, short_repr as short_repr, strings as strings
from deepdiff.path import GET as GET, GETATTR as GETATTR
from deepdiff.serialization import pickle_dump as pickle_dump, pickle_load as pickle_load

logger: Incomplete
VERIFICATION_MSG: str
ELEM_NOT_FOUND_TO_ADD_MSG: str
TYPE_CHANGE_FAIL_MSG: str
VERIFY_SYMMETRY_MSG: str
FAIL_TO_REMOVE_ITEM_IGNORE_ORDER_MSG: str
DELTA_NUMPY_OPERATOR_OVERRIDE_MSG: str
BINIARY_MODE_NEEDED_MSG: str
DELTA_AT_LEAST_ONE_ARG_NEEDED: str
INVALID_ACTION_WHEN_CALLING_GET_ELEM: str
INVALID_ACTION_WHEN_CALLING_SIMPLE_SET_ELEM: str
INVALID_ACTION_WHEN_CALLING_SIMPLE_DELETE_ELEM: str
UNABLE_TO_GET_ITEM_MSG: str
UNABLE_TO_GET_PATH_MSG: str
INDEXES_NOT_FOUND_WHEN_IGNORE_ORDER: str
NUMPY_TO_LIST: str
NOT_VALID_NUMPY_TYPE: str
doc: Incomplete

class DeltaError(ValueError): ...
class DeltaNumpyOperatorOverrideError(ValueError): ...

class Delta:
    __doc__ = doc
    diff: Incomplete
    mutate: Incomplete
    verify_symmetry: Incomplete
    raise_errors: Incomplete
    log_errors: Incomplete
    serializer: Incomplete
    deserializer: Incomplete
    def __init__(self, diff: Incomplete | None = ..., delta_path: Incomplete | None = ..., delta_file: Incomplete | None = ..., deserializer=..., log_errors: bool = ..., mutate: bool = ..., raise_errors: bool = ..., safe_to_import: Incomplete | None = ..., serializer=..., verify_symmetry: bool = ...) -> None: ...
    post_process_paths_to_convert: Incomplete
    def reset(self) -> None: ...
    root: Incomplete
    def __add__(self, other): ...
    __radd__ = __add__
    def dump(self, file) -> None: ...
    def dumps(self): ...
    def to_dict(self): ...
