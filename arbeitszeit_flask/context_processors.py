from typing import Any

from arbeitszeit.use_cases.list_available_languages import ListAvailableLanguagesUseCase
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.www.presenters.list_available_languages_presenter import (
    ListAvailableLanguagesPresenter,
)


@with_injection()
def add_template_variables(
    list_languages_use_case: ListAvailableLanguagesUseCase,
    list_languages_presenter: ListAvailableLanguagesPresenter,
) -> dict[str, Any]:
    use_case_request = list_languages_use_case.Request()
    use_case_response = list_languages_use_case.list_available_languages(
        use_case_request
    )
    view_model = list_languages_presenter.present_available_languages_list(
        use_case_response
    )
    return dict(languages=view_model)
