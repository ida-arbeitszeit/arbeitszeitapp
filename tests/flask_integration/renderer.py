from typing import Any, Dict, Optional, Set


class FakeTemplateRenderer:
    """Used for testing the properties of renderers that internally call
    another renderer.
    """

    def __init__(self) -> None:
        self._templates: Dict[str, str] = dict()
        self.previouse_render_context: Set[str] = set()

    def register_template(self, name: str, content: str = "test content") -> None:
        self._templates[name] = content

    def render_template(
        self, name: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        if context is None:
            self.previouse_render_context = set()
        else:
            self.previouse_render_context = set(context.keys())
        return self._templates[name]
