from typing import Dict


# hex values should be same as bulma values
_colors = {
    "primary": "#00d1b2",
    "info": "#3e8ed0",
    "warning": "#ffe08a",
    "danger": "#f14668",
    "success": "#48c78e",
}


class FlaskColors:
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
