from flask_profiler.presenters import get_summary_presenter as presenter
from flask_profiler.response import HttpResponse as HttpResponse

class GetSummaryView:
    def render_view_model(self, view_model: presenter.ViewModel) -> HttpResponse: ...
