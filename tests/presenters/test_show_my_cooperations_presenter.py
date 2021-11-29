from unittest import TestCase

from arbeitszeit_web.show_my_cooperations import ShowMyCooperationsPresenter


class ShowMyCooperationsPresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = ShowMyCooperationsPresenter()
