from typing import Dict


class FlaskColors:
    def __init__(self) -> None:
        # hex values should be same as bulma values
        self.all_colors = {
            "primary": "#00d1b2",
            "info": "#3e8ed0",
            "warning": "#ffe08a",
            "danger": "#f14668",
            "success": "#48c78e",
        }

    @property
    def primary(self) -> str:
        return self.all_colors["primary"]

    @property
    def info(self) -> str:
        return self.all_colors["info"]

    @property
    def warning(self) -> str:
        return self.all_colors["warning"]

    @property
    def danger(self) -> str:
        return self.all_colors["danger"]

    @property
    def success(self) -> str:
        return self.all_colors["success"]

    def get_all_defined_colors(self) -> Dict[str, str]:
        return self.all_colors
