"""This module shall contain a mock implementation of the UrlIndex."""

from typing import Any, Callable
from urllib.parse import quote


class UrlIndexMethod:
    def __set_name__(self, owner, name: str) -> None:
        self._attribute_name = name

    def __get__(self, obj: Any, objtype=None) -> Callable[..., str]:
        def method(*args, **kwargs) -> str:
            sorted_args = sorted(list(map(str, args)))
            sorted_kwargs = sorted(
                [f"{key}: {str(value)}" for key, value in kwargs.items()]
            )
            url = f"url://{quote(self._attribute_name)}"
            url += f'/args/{"/".join(map(quote, sorted_args))}' if sorted_args else ""
            url += (
                f'/kwargs/{"/".join(map(lambda t: quote(str(t)), sorted_kwargs))}'
                if sorted_kwargs
                else ""
            )
            return url

        return method


class UrlIndexTestImpl:
    """This implementation of a UrlIndex is not required to return
    valid link targets.  Its main purpose is in testing whether the
    correct link target is used in hyperlink generation.  The
    UrlIndexMethod descriptor should take care of generating strings
    that are unique with respect to specified arguments and method
    names.
    """

    get_accountant_dashboard_url = UrlIndexMethod()
    get_accountant_invitation_url = UrlIndexMethod()
    get_answer_company_work_invite_url = UrlIndexMethod()
    get_approve_plan_url = UrlIndexMethod()
    get_change_email_url = UrlIndexMethod()
    get_company_account_a_url = UrlIndexMethod()
    get_company_account_p_url = UrlIndexMethod()
    get_company_account_r_url = UrlIndexMethod()
    get_company_account_prd_url = UrlIndexMethod()
    get_company_accounts_url = UrlIndexMethod()
    get_company_confirmation_url = UrlIndexMethod()
    get_company_dashboard_url = UrlIndexMethod()
    get_company_dashboard_url = UrlIndexMethod()
    get_company_summary_url = UrlIndexMethod()
    get_company_transactions_url = UrlIndexMethod()
    get_coop_summary_url = UrlIndexMethod()
    get_create_draft_url = UrlIndexMethod()
    get_delete_draft_url = UrlIndexMethod()
    get_draft_details_url = UrlIndexMethod()
    get_draft_list_url = UrlIndexMethod()
    get_draft_list_url = UrlIndexMethod()
    get_end_coop_url = UrlIndexMethod()
    get_file_plan_url = UrlIndexMethod()
    get_global_barplot_for_certificates_url = UrlIndexMethod()
    get_global_barplot_for_means_of_production_url = UrlIndexMethod()
    get_global_barplot_for_plans_url = UrlIndexMethod()
    get_hide_plan_url = UrlIndexMethod()
    get_language_change_url = UrlIndexMethod()
    get_line_plot_of_company_a_account = UrlIndexMethod()
    get_line_plot_of_company_p_account = UrlIndexMethod()
    get_line_plot_of_company_prd_account = UrlIndexMethod()
    get_line_plot_of_company_r_account = UrlIndexMethod()
    get_list_of_coordinators_url = UrlIndexMethod()
    get_member_confirmation_url = UrlIndexMethod()
    get_member_dashboard_url = UrlIndexMethod()
    get_my_plan_drafts_url = UrlIndexMethod()
    get_my_plans_url = UrlIndexMethod()
    get_plan_details_url = UrlIndexMethod()
    get_query_companies_url = UrlIndexMethod()
    get_query_plans_url = UrlIndexMethod()
    get_register_private_consumption_url = UrlIndexMethod()
    get_register_productive_consumption_url = UrlIndexMethod()
    get_renew_plan_url = UrlIndexMethod()
    get_request_coop_url = UrlIndexMethod()
    get_request_coordination_transfer_url = UrlIndexMethod()
    get_request_change_email_url = UrlIndexMethod()
    get_revoke_plan_filing_url = UrlIndexMethod()
    get_show_coordination_transfer_request_url = UrlIndexMethod()
    get_unconfirmed_member_url = UrlIndexMethod()
    get_unreviewed_plans_list_view_url = UrlIndexMethod()
    get_user_account_details_url = UrlIndexMethod()
    get_work_invite_url = UrlIndexMethod()
