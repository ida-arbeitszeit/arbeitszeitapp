class ColorsTestImpl:
    def __init__(self) -> None:
        self.all_colors = {
            "primary": "primary_color",
            "info": "info_color",
            "warning": "warning_color",
            "danger": "danger_color",
            "success": "success_color",
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
