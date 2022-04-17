from typing import Dict

_colors = {
    "primary": "primary_color",
    "info": "info_color",
    "warning": "warning_color",
    "danger": "danger_color",
    "success": "success_color",
}


class TestColors:
    @property
    def primary(self) -> str:
        return _colors["primary"]

    @property
    def info(self) -> str:
        return _colors["info"]

    @property
    def warning(self) -> str:
        return _colors["warning"]

    @property
    def danger(self) -> str:
        return _colors["danger"]

    @property
    def success(self) -> str:
        return _colors["success"]

    def get_dict(self) -> Dict[str, str]:
        return _colors
