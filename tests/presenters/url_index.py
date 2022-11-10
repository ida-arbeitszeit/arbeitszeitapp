"""This module shall contain a mock implementation of the UrlIndex."""

from typing import Any, Callable
from uuid import UUID


class UrlIndexMethod:
    def __set_name__(self, owner, name: str) -> None:
        self._attribute_name = name

    def __get__(self, obj: Any, objtype=None) -> Callable[..., str]:
        def method(*args, **kwargs) -> str:
            sorted_args = list(map(str, args))
            sorted_args.sort()
            sorted_kwargs = [f"{key}: {value}" for key, value in kwargs.items()]
            sorted_kwargs.sort()
            return f"url index placeholder text for {self._attribute_name}, context: args={sorted_args}, kwargs={','.join(sorted_kwargs)}"

        return method


class UrlIndexTestImpl:
    """This implementation of a UrlIndex is not required to return
    valid link targets.  Its main purpose is in testing whether the
    correct link target is used in hyperlink generation.  The
    UrlIndexMethod descriptor should take care of generating strings
    that are unique with respect to specified arguments and method
    names.
    """

    get_plan_summary_url = UrlIndexMethod()
    get_member_dashboard_url = UrlIndexMethod()
    get_work_invite_url = UrlIndexMethod()
    get_company_summary_url = UrlIndexMethod()
    get_coop_summary_url = UrlIndexMethod()
    get_company_dashboard_url = UrlIndexMethod()
    get_draft_list_url = UrlIndexMethod()
    get_draft_summary_url = UrlIndexMethod()
    get_answer_company_work_invite_url = UrlIndexMethod()
    get_global_barplot_for_certificates_url = UrlIndexMethod()
    get_global_barplot_for_means_of_production_url = UrlIndexMethod()
    get_global_barplot_for_plans_url = UrlIndexMethod()
    get_line_plot_of_company_prd_account = UrlIndexMethod()
    get_line_plot_of_company_r_account = UrlIndexMethod()
    get_line_plot_of_company_p_account = UrlIndexMethod()
    get_line_plot_of_company_a_account = UrlIndexMethod()
    get_pay_consumer_product_url = UrlIndexMethod()
    get_pay_means_of_production_url = UrlIndexMethod()
    get_toggle_availability_url = UrlIndexMethod()
    get_request_coop_url = UrlIndexMethod()
    get_end_coop_url = UrlIndexMethod()
    get_delete_draft_url = UrlIndexMethod()
    get_accountant_dashboard_url = UrlIndexMethod()
    get_my_plans_url = UrlIndexMethod()
    get_file_plan_url = UrlIndexMethod()
    get_unreviewed_plans_list_view_url = UrlIndexMethod()
    get_approve_plan_url = UrlIndexMethod()

    def get_member_confirmation_url(self, *, token: str) -> str:
        return f"get_member_confirmation_url {token}"

    def get_company_confirmation_url(self, *, token: str) -> str:
        return f"get_company_confirmation_url {token}"


class RenewPlanUrlIndexTestImpl:
    def get_renew_plan_url(self, plan_id: UUID) -> str:
        return f"fake_renew_url:{plan_id}"


class HidePlanUrlIndexTestImpl:
    def get_hide_plan_url(self, plan_id: UUID) -> str:
        return f"fake_hide_plan_url:{plan_id}"


class AccountantInvitationUrlIndexImpl:
    def get_accountant_invitation_url(self, token: str) -> str:
        return f"accountant invitation {token} url"


class LanguageChangerUrlIndexImpl:
    def get_language_change_url(self, language_code: str) -> str:
        return f"language change url for {language_code}"
