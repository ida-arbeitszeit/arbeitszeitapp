from typing import Any

from arbeitszeit_flask.config.options import ConfigOption


class ConfigOptionMissing(Exception):
    pass


class ConfigOptionTypeInvalid(Exception):
    pass


class ConfigValidator:
    def __init__(self, config: dict, expected_options: set[ConfigOption]) -> None:
        self._config = config
        self._expected_options = expected_options

    def validate_options(self) -> None:
        for entry in self._expected_options:
            if entry.name not in self._config:
                raise ConfigOptionMissing(f"Missing configuration option: {entry.name}")

    def validate_option_types(self) -> None:
        for entry in self._expected_options:

            value = self._config[entry.name]
            convertible = False

            for expected_type in entry.converts_to_types:
                try:
                    if expected_type is bool:
                        convertible = self._is_boolean(value)
                        if convertible:
                            break
                    elif expected_type is int:
                        convertible = self._is_integer(value)
                        if convertible:
                            break
                    else:
                        expected_type(value)
                        convertible = True
                        break
                except (ValueError, TypeError):
                    continue

            if not convertible:
                expected_types_str = ", ".join(
                    [t.__name__ for t in entry.converts_to_types]
                )
                raise ConfigOptionTypeInvalid(
                    f"Configuration option {entry.name} has value {value!r} that cannot be converted to any of the expected types: {expected_types_str}"
                )

    def _is_boolean(self, value: Any) -> bool:
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            return value.lower() in ("true", "false", "1", "0")
        if isinstance(value, int):
            return value in (0, 1)
        return False

    def _is_integer(self, value: Any) -> bool:
        if isinstance(value, int):
            return True
        if isinstance(value, str):
            return value.isdigit() or (value.startswith("-") and value[1:].isdigit())
        return False
