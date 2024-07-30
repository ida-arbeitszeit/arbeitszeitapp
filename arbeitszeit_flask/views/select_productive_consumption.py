from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import render_template, request

from arbeitszeit_flask.forms import RegisterProductiveConsumptionForm
from arbeitszeit_flask.types import Response


@dataclass
class SelectProductiveConsumptionView:
    def GET(self) -> Response:
        form = RegisterProductiveConsumptionForm(request.form)
        plan_id: str | None = request.args.get("plan_id")
        if plan_id:
            form.plan_id_field().set_value(plan_id)
        return FlaskResponse(
            render_template("company/select_productive_consumption.html", form=form),
            status=200,
        )
