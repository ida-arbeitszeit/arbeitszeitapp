from flask import Blueprint
from flask_restx import Api

from arbeitszeit_flask.extensions import csrf_protect

from .auth import namespace as auth_ns
from .companies import namespace as companies_ns
from .plans import namespace as plans_ns

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")

api_extension = Api(
    app=blueprint,
    title="Arbeitszeitapp API",
    version="0.1",
    description="The JSON API of Arbeitszeitapp.",
    doc="/doc/",
    decorators=[csrf_protect.exempt],
)

api_extension.add_namespace(plans_ns)
api_extension.add_namespace(companies_ns)
api_extension.add_namespace(auth_ns)
