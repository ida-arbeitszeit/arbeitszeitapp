from decimal import Decimal
from uuid import UUID

from flask import Blueprint, Response, request
from flask_login import login_required

from arbeitszeit.use_cases import show_a_account_details, show_r_account_details
from arbeitszeit.use_cases.show_p_account_details import ShowPAccountDetailsUseCase
from arbeitszeit.use_cases.show_prd_account_details import ShowPRDAccountDetailsUseCase
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.colors import Colors
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.www.controllers.show_a_account_details_controller import (
    ShowAAccountDetailsController,
)

plots = Blueprint("plots", __name__)


@plots.route("/plots/global_barplot_for_certificates")
@with_injection()
@login_required
def global_barplot_for_certificates(
    plotter: Plotter, translator: Translator, colors: Colors
):
    certificates_count = Decimal(request.args["certificates_count"])
    available_product = Decimal(request.args["available_product"])
    png = plotter.create_bar_plot(
        x_coordinates=[
            translator.gettext("Work certificates"),
            translator.gettext("Available product"),
        ],
        height_of_bars=[
            certificates_count,
            available_product,
        ],
        colors_of_bars=[colors.primary, colors.info],
        fig_size=(5, 4),
        y_label=translator.gettext("Hours"),
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/global_barplot_for_means_of_production")
@with_injection()
@login_required
def global_barplot_for_means_of_production(
    plotter: Plotter, translator: Translator, colors: Colors
):
    planned_means = Decimal(request.args["planned_means"])
    planned_resources = Decimal(request.args["planned_resources"])
    planned_work = Decimal(request.args["planned_work"])
    png = plotter.create_bar_plot(
        x_coordinates=[
            translator.pgettext("Text should be short", "Fixed means"),
            translator.pgettext("Text should be short", "Liquid means"),
            translator.gettext("Work"),
        ],
        height_of_bars=[
            planned_means,
            planned_resources,
            planned_work,
        ],
        colors_of_bars=[
            colors.primary,
            colors.info,
            colors.danger,
        ],
        fig_size=(5, 4),
        y_label=translator.gettext("Hours"),
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/global_barplot_for_plans")
@with_injection()
@login_required
def global_barplot_for_plans(plotter: Plotter, translator: Translator, colors: Colors):
    productive_plans = Decimal(request.args["productive_plans"])
    public_plans = Decimal(request.args["public_plans"])
    png = plotter.create_bar_plot(
        x_coordinates=[
            translator.gettext("Productive plans"),
            translator.gettext("Public plans"),
        ],
        height_of_bars=[productive_plans, public_plans],
        colors_of_bars=list(colors.get_all_defined_colors().values()),
        fig_size=(5, 4),
        y_label=translator.gettext("Amount"),
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/line_plot_of_company_prd_account")
@with_injection()
@login_required
def line_plot_of_company_prd_account(
    plotter: Plotter,
    use_case: ShowPRDAccountDetailsUseCase,
):
    company_id = UUID(request.args["company_id"])
    use_case_response = use_case(company_id)
    png = plotter.create_line_plot(
        x=use_case_response.plot.timestamps,
        y=use_case_response.plot.accumulated_volumes,
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/line_plot_of_company_r_account")
@with_injection()
@login_required
def line_plot_of_company_r_account(
    plotter: Plotter,
    use_case: show_r_account_details.ShowRAccountDetailsUseCase,
):
    use_case_request = show_r_account_details.Request(
        company=UUID(request.args["company_id"])
    )
    use_case_response = use_case.show_details(request=use_case_request)
    png = plotter.create_line_plot(
        x=use_case_response.plot.timestamps,
        y=use_case_response.plot.accumulated_volumes,
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/line_plot_of_company_p_account")
@with_injection()
@login_required
def line_plot_of_company_p_account(
    plotter: Plotter,
    use_case: ShowPAccountDetailsUseCase,
):
    use_case_request = ShowPAccountDetailsUseCase.Request(
        company=UUID(request.args["company_id"])
    )
    use_case_response = use_case.show_details(request=use_case_request)
    png = plotter.create_line_plot(
        x=use_case_response.plot.timestamps,
        y=use_case_response.plot.accumulated_volumes,
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/line_plot_of_company_a_account")
@with_injection()
@login_required
def line_plot_of_company_a_account(
    plotter: Plotter,
    controller: ShowAAccountDetailsController,
    use_case: show_a_account_details.ShowAAccountDetailsUseCase,
):
    company_id = UUID(request.args["company_id"])
    use_case_request = controller.create_request(company_id)
    use_case_response = use_case.show_details(request=use_case_request)
    png = plotter.create_line_plot(
        x=use_case_response.plot.timestamps,
        y=use_case_response.plot.accumulated_volumes,
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)
