from dataclasses import dataclass
from typing import Optional, Protocol

from arbeitszeit.use_cases.query_plans import PlanFilter, PlanSorting, QueryPlansRequest
from arbeitszeit_web.pagination import DEFAULT_PAGE_SIZE, PAGE_PARAMETER_NAME
from arbeitszeit_web.request import Request


class QueryPlansFormData(Protocol):
    def get_query_string(self) -> str: ...

    def get_category_string(self) -> str: ...

    def get_radio_string(self) -> str: ...

    def get_checkbox_value(self) -> bool: ...


@dataclass
class QueryPlansController:
    def import_form_data(
        self,
        form: Optional[QueryPlansFormData] = None,
        request: Optional[Request] = None,
    ) -> QueryPlansRequest:
        if form is None:
            query = None
            filter_category = PlanFilter.by_product_name
            sorting_category = PlanSorting.by_activation
            include_expired_plans = False
        else:
            query = form.get_query_string().strip() or None
            filter_category = self._import_filter_category(form)
            sorting_category = self._import_sorting_category(form)
            include_expired_plans = self._import_include_expired(form)
        offset = self._get_pagination_offset(request) if request else 0
        return QueryPlansRequest(
            query_string=query,
            filter_category=filter_category,
            sorting_category=sorting_category,
            include_expired_plans=include_expired_plans,
            offset=offset,
            limit=DEFAULT_PAGE_SIZE,
        )

    def _get_pagination_offset(self, request: Request) -> int:
        page_str = request.query_string().get_last_value(PAGE_PARAMETER_NAME)
        if page_str is None:
            return 0
        try:
            page_number = int(page_str)
        except ValueError:
            return 0
        return (page_number - 1) * DEFAULT_PAGE_SIZE

    def _import_filter_category(self, form: QueryPlansFormData) -> PlanFilter:
        if form.get_category_string() == "Plan-ID":
            filter_category = PlanFilter.by_plan_id
        else:
            filter_category = PlanFilter.by_product_name
        return filter_category

    def _import_sorting_category(self, form: QueryPlansFormData) -> PlanSorting:
        sorting = form.get_radio_string()
        if sorting == "company_name":
            sorting_category = PlanSorting.by_company_name
        else:
            sorting_category = PlanSorting.by_activation
        return sorting_category

    def _import_include_expired(self, form: QueryPlansFormData) -> bool:
        return form.get_checkbox_value()
