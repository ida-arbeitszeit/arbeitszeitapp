from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.list_workers import ListWorkersResponse


class ListWorkersPresenter:
    @dataclass
    class Worker:
        name: str
        id: str

    @dataclass
    class ViewModel:
        is_show_workers: bool
        workers: List[ListWorkersPresenter.Worker]

    def show_workers_list(self, use_case_response: ListWorkersResponse) -> ViewModel:
        return self.ViewModel(
            is_show_workers=bool(use_case_response.workers),
            workers=[
                self.Worker(name=worker.name, id=str(worker.id))
                for worker in use_case_response.workers
            ],
        )
