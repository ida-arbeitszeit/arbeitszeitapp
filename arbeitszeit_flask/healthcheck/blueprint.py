from flask import Blueprint

from arbeitszeit_flask.class_based_view import as_flask_view
from arbeitszeit_flask.views.healthcheck_view import HealthcheckView

# Create a blueprint for health checks that doesn't require authentication
healthcheck_blueprint = Blueprint("healthcheck", __name__)

# Register the health check endpoint
healthcheck_blueprint.route("/health", methods=["GET"])(as_flask_view()(HealthcheckView))
