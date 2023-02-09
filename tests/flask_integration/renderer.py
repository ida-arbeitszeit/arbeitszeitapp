from typing import Any, Dict, Optional

from arbeitszeit.injector import singleton


@singleton
class FakeTemplateRenderer:
    """Used for testing the properties of renderers that internally call
    another renderer.
    """

    def __init__(self) -> None:
        self._templates: Dict[str, str] = dict()
        self.previous_render_context: Dict[str, Any] = dict()

    def register_template(self, name: str, content: str = "test content") -> None:
        self._templates[name] = content

    def render_template(
        self, name: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        if context is None:
            self.previous_render_context = dict()
        else:
            self.previous_render_context = context
        return self._templates[name]
