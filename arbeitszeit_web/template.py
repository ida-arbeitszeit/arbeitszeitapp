from typing import Any, Dict, Optional, Protocol


class TemplateRenderer(Protocol):
    def render_template(
        self, name: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        pass
