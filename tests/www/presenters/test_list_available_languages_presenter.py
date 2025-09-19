from arbeitszeit.interactors.list_available_languages import (
    ListAvailableLanguagesInteractor,
)
from arbeitszeit_web.www.presenters.list_available_languages_presenter import (
    ListAvailableLanguagesPresenter,
)
from tests.language_service import FakeLanguageService
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListAvailableLanguagesPresenter)
        self.language_service = self.injector.get(FakeLanguageService)

    def test_dont_show_language_listing_if_no_languages_are_available(self) -> None:
        interactor_response = ListAvailableLanguagesInteractor.Response(
            available_language_codes=[]
        )
        view_model = self.presenter.present_available_languages_list(
            interactor_response
        )
        self.assertFalse(view_model.show_language_listing)

    def test_show_languages_listing_if_at_least_one_language_is_available(self) -> None:
        interactor_response = ListAvailableLanguagesInteractor.Response(
            available_language_codes=["ru"]
        )
        view_model = self.presenter.present_available_languages_list(
            interactor_response
        )
        self.assertTrue(view_model.show_language_listing)

    def test_that_one_language_item_is_listed_when_response_contains_also_one(
        self,
    ) -> None:
        interactor_response = ListAvailableLanguagesInteractor.Response(
            available_language_codes=["ru"]
        )
        view_model = self.presenter.present_available_languages_list(
            interactor_response
        )
        self.assertEqual(len(view_model.languages_listing), 1)

    def test_that_two_language_items_are_listed_when_response_contains_also_two(
        self,
    ) -> None:
        interactor_response = ListAvailableLanguagesInteractor.Response(
            available_language_codes=["ru", "zh"]
        )
        view_model = self.presenter.present_available_languages_list(
            interactor_response
        )
        self.assertEqual(len(view_model.languages_listing), 2)

    def test_that_language_code_ru_is_resolved_to_correct_change_link(self) -> None:
        interactor_response = ListAvailableLanguagesInteractor.Response(
            available_language_codes=["ru"],
        )
        view_model = self.presenter.present_available_languages_list(
            interactor_response
        )
        self.assertEqual(
            view_model.languages_listing[0].change_url,
            self.url_index.get_language_change_url("ru"),
        )

    def test_that_language_code_en_is_resolved_to_correct_change_link(self) -> None:
        interactor_response = ListAvailableLanguagesInteractor.Response(
            available_language_codes=["en"],
        )
        view_model = self.presenter.present_available_languages_list(
            interactor_response
        )
        self.assertEqual(
            view_model.languages_listing[0].change_url,
            self.url_index.get_language_change_url("en"),
        )

    def test_language_name_is_properly_rendered_if_it_can_be_retrieved(self) -> None:
        interactor_response = ListAvailableLanguagesInteractor.Response(
            available_language_codes=["en"],
        )
        self.language_service.set_language_name("en", "english")
        view_model = self.presenter.present_available_languages_list(
            interactor_response
        )
        self.assertEqual(
            view_model.languages_listing[0].label,
            "english",
        )

    def test_language_name_is_lang_code_if_name_cannot_be_retrieved(self) -> None:
        interactor_response = ListAvailableLanguagesInteractor.Response(
            available_language_codes=["en"],
        )
        self.language_service.set_language_name("en", None)
        view_model = self.presenter.present_available_languages_list(
            interactor_response
        )
        self.assertEqual(
            view_model.languages_listing[0].label,
            "en",
        )
