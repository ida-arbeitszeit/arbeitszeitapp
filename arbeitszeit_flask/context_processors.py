from typing import Any

from arbeitszeit.interactors.list_available_languages import (
    ListAvailableLanguagesInteractor,
)
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.www.presenters.list_available_languages_presenter import (
    ListAvailableLanguagesPresenter,
)


@with_injection()
def add_template_variables(
    list_languages_interactor: ListAvailableLanguagesInteractor,
    list_languages_presenter: ListAvailableLanguagesPresenter,
) -> dict[str, Any]:
    interactor_request = list_languages_interactor.Request()
    interactor_response = list_languages_interactor.list_available_languages(
        interactor_request
    )
    view_model = list_languages_presenter.present_available_languages_list(
        interactor_response
    )
    return dict(languages=view_model)
