from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.list_workers import ListWorkersResponse
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ListWorkersPresenter:
    url_index: UrlIndex

    @dataclass
    class Worker:
        name: str
        id: str

    @dataclass
    class ViewModel:
        workers: List[ListWorkersPresenter.Worker]
        url_to_remove_workers: str
        url_to_pending_work_invites: str

    def show_workers_list(self, use_case_response: ListWorkersResponse) -> ViewModel:
        return self.ViewModel(
            workers=[
                self.Worker(name=worker.name, id=str(worker.id))
                for worker in use_case_response.workers
            ],
            url_to_remove_workers=self.url_index.get_remove_worker_from_company_url(),
            url_to_pending_work_invites=self.url_index.get_pending_work_invites_url(),
        )
