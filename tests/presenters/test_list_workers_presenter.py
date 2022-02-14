from typing import Optional
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.use_cases.list_workers import ListedWorker, ListWorkersResponse
from arbeitszeit_web.presenters.list_workers_presenter import ListWorkersPresenter


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = ListWorkersPresenter()

    def test_that_view_model_does_not_contains_workers_if_response_didnt_either(
        self,
    ) -> None:
        view_model = self.presenter.show_workers_list(self.create_empty_response())
        self.assertFalse(view_model.workers)

    def test_that_view_model_does_not_show_workers_list_if_response_contains_no_workers(
        self,
    ) -> None:
        view_model = self.presenter.show_workers_list(self.create_empty_response())
        self.assertFalse(view_model.is_show_workers)

    def test_that_view_model_contains_workers_if_response_also_does(self) -> None:
        view_model = self.presenter.show_workers_list(self.create_response(workers=1))
        self.assertTrue(view_model.workers)

    def test_that_view_model_shows_workers_if_response_contains_one_worker(
        self,
    ) -> None:
        view_model = self.presenter.show_workers_list(self.create_response(workers=1))
        self.assertTrue(view_model.is_show_workers)

    def test_that_view_model_contains_3_workers_if_response_also_contains_3(
        self,
    ) -> None:
        view_model = self.presenter.show_workers_list(self.create_response(workers=3))
        self.assertEqual(len(view_model.workers), 3)

    def test_view_model_contains_correct_name_of_given_worker(self) -> None:
        view_model = self.presenter.show_workers_list(
            self.create_one_worker_response(name="test worker name")
        )
        self.assertEqual(view_model.workers[0].name, "test worker name")

    def test_that_correct_uuid_is_shown(self) -> None:
        expected_id = uuid4()
        view_model = self.presenter.show_workers_list(
            self.create_one_worker_response(id=expected_id),
        )
        self.assertEqual(
            view_model.workers[0].id,
            str(expected_id),
        )

    def create_empty_response(self) -> ListWorkersResponse:
        return ListWorkersResponse([])

    def create_response(self, workers: int) -> ListWorkersResponse:
        return ListWorkersResponse(
            [
                ListedWorker(id=uuid4(), name="test worker", email="test@mail.test")
                for _ in range(workers)
            ]
        )

    def create_one_worker_response(
        self, name: str = "t", id: Optional[UUID] = None
    ) -> ListWorkersResponse:
        if id is None:
            id = uuid4()
        return ListWorkersResponse(
            workers=[ListedWorker(id=id, name=name, email="test@test.test")]
        )
