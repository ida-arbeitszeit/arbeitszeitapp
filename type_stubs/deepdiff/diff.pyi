from typing import Any

logger: Any
MAX_PASSES_REACHED_MSG: str
MAX_DIFFS_REACHED_MSG: str
notpresent_indexed: Any
doc: Any
PROGRESS_MSG: str
DISTANCE_CACHE_HIT_COUNT: str
DIFF_COUNT: str
PASSES_COUNT: str
MAX_PASS_LIMIT_REACHED: str
MAX_DIFF_LIMIT_REACHED: str
DISTANCE_CACHE_ENABLED: str
PREVIOUS_DIFF_COUNT: str
PREVIOUS_DISTANCE_CACHE_HIT_COUNT: str
CANT_FIND_NUMPY_MSG: str
INVALID_VIEW_MSG: str
CUTOFF_RANGE_ERROR_MSG: str
VERBOSE_LEVEL_RANGE_MSG: str
PURGE_LEVEL_RANGE_MSG: str
CUTOFF_DISTANCE_FOR_PAIRS_DEFAULT: float
CUTOFF_INTERSECTION_FOR_PAIRS_DEFAULT: float
DEEPHASH_PARAM_KEYS: Any

class DeepDiff:
    __doc__: Any
    CACHE_AUTO_ADJUST_THRESHOLD: float
    custom_operators: Any
    ignore_order: Any
    ignore_order_func: Any
    ignore_numeric_type_changes: Any
    ignore_string_type_changes: Any
    ignore_type_in_groups: Any
    report_repetition: Any
    exclude_paths: Any
    include_paths: Any
    exclude_regex_paths: Any
    exclude_types: Any
    exclude_types_tuple: Any
    ignore_type_subclasses: Any
    type_check_func: Any
    ignore_string_case: Any
    exclude_obj_callback: Any
    exclude_obj_callback_strict: Any
    include_obj_callback: Any
    include_obj_callback_strict: Any
    number_to_string: Any
    iterable_compare_func: Any
    ignore_private_variables: Any
    ignore_nan_inequality: Any
    hasher: Any
    cache_tuning_sample_size: Any
    group_by: Any
    encodings: Any
    ignore_encoding_errors: Any
    significant_digits: Any
    math_epsilon: Any
    truncate_datetime: Any
    number_format_notation: Any
    verbose_level: Any
    view: Any
    max_passes: Any
    max_diffs: Any
    cutoff_distance_for_pairs: Any
    cutoff_intersection_for_pairs: Any
    progress_logger: Any
    cache_size: Any
    is_root: bool
    hashes: Any
    deephash_parameters: Any
    tree: Any
    t1: Any
    t2: Any
    def __init__(
        self,
        t1,
        t2,
        cache_purge_level: int = ...,
        cache_size: int = ...,
        cache_tuning_sample_size: int = ...,
        custom_operators: Any | None = ...,
        cutoff_distance_for_pairs=...,
        cutoff_intersection_for_pairs=...,
        encodings: Any | None = ...,
        exclude_obj_callback: Any | None = ...,
        exclude_obj_callback_strict: Any | None = ...,
        exclude_paths: Any | None = ...,
        include_obj_callback: Any | None = ...,
        include_obj_callback_strict: Any | None = ...,
        include_paths: Any | None = ...,
        exclude_regex_paths: Any | None = ...,
        exclude_types: Any | None = ...,
        get_deep_distance: bool = ...,
        group_by: Any | None = ...,
        hasher: Any | None = ...,
        hashes: Any | None = ...,
        ignore_encoding_errors: bool = ...,
        ignore_nan_inequality: bool = ...,
        ignore_numeric_type_changes: bool = ...,
        ignore_order: bool = ...,
        ignore_order_func: Any | None = ...,
        ignore_private_variables: bool = ...,
        ignore_string_case: bool = ...,
        ignore_string_type_changes: bool = ...,
        ignore_type_in_groups: Any | None = ...,
        ignore_type_subclasses: bool = ...,
        iterable_compare_func: Any | None = ...,
        log_frequency_in_sec: int = ...,
        math_epsilon: Any | None = ...,
        max_diffs: Any | None = ...,
        max_passes: int = ...,
        number_format_notation: str = ...,
        number_to_string_func: Any | None = ...,
        progress_logger=...,
        report_repetition: bool = ...,
        significant_digits: Any | None = ...,
        truncate_datetime: Any | None = ...,
        verbose_level: int = ...,
        view=...,
        _original_type: Any | None = ...,
        _parameters: Any | None = ...,
        _shared_parameters: Any | None = ...,
        **kwargs,
    ): ...
    def custom_report_result(
        self, report_type, level, extra_info: Any | None = ...
    ) -> None: ...
    def get_stats(self): ...
    @property
    def affected_paths(self): ...
    @property
    def affected_root_keys(self): ...
