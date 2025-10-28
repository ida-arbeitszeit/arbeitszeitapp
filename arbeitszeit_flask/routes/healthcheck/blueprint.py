from flask import Blueprint

from arbeitszeit_flask.class_based_view import as_flask_view
from arbeitszeit_flask.views.healthcheck_view import HealthcheckView

healthcheck_blueprint = Blueprint("healthcheck", __name__)

healthcheck_blueprint.route("/health", methods=["GET"])(
    as_flask_view()(HealthcheckView)
)
