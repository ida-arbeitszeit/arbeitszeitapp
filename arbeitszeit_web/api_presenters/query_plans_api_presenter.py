from dataclasses import asdict

from arbeitszeit.use_cases.query_plans import PlanQueryResponse
from arbeitszeit_web.json_handling import serialize_to_json


class QueryPlansApiPresenter:
    def get_json(self, use_case_response: PlanQueryResponse) -> str:
        dictionary = asdict(use_case_response)
        json_string = serialize_to_json(dictionary)
        return json_string
