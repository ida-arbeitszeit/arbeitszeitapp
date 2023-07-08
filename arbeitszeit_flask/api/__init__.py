from flask import Blueprint
from flask_restx import Api

from arbeitszeit_flask.extensions import csrf_protect

from .auth import namespace as auth_ns
from .companies import namespace as companies_ns
from .plans import namespace as plans_ns

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")

DESCRIPTION = """
The JSON API of Arbeitszeitapp.

**Authentication:**

Please use a session (e.g. making use of 'requests.session') and log in via the 'auth/login_member' or 'auth/login_company' before requesting ressources.

If you have no account yet, you have to register via the webapp first.
"""

api_extension = Api(
    app=blueprint,
    title="Arbeitszeitapp API",
    version="0.1",
    description=DESCRIPTION,
    doc="/doc/",
    decorators=[csrf_protect.exempt],
)

api_extension.add_namespace(plans_ns)
api_extension.add_namespace(companies_ns)
api_extension.add_namespace(auth_ns)
