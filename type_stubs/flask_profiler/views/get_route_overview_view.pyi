from flask_profiler.presenters import get_route_overview_presenter as presenter
from flask_profiler.response import HttpResponse as HttpResponse

class GetRouteOverviewView:
    def render_view_model(self, view_model: presenter.ViewModel) -> HttpResponse: ...
