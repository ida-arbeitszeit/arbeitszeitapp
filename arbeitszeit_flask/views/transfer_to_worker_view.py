from dataclasses import dataclass
from uuid import UUID

from flask import Response
from flask_login import current_user

from arbeitszeit.use_cases.list_workers import ListWorkers, ListWorkersRequest
from arbeitszeit.use_cases.send_work_certificates_to_worker import (
    SendWorkCertificatesToWorker,
)
from arbeitszeit_flask.template import TemplateRenderer
from arbeitszeit_web.www.controllers.send_work_certificates_to_worker_controller import (
    ControllerRejection,
    SendWorkCertificatesToWorkerController,
)
from arbeitszeit_web.www.presenters.send_work_certificates_to_worker_presenter import (
    SendWorkCertificatesToWorkerPresenter,
)


@dataclass
class TransferToWorkerView:
    template_renderer: TemplateRenderer
    send_work_certificates_to_worker: SendWorkCertificatesToWorker
    controller: SendWorkCertificatesToWorkerController
    presenter: SendWorkCertificatesToWorkerPresenter
    list_workers: ListWorkers

    def respond_to_get(self) -> Response:
        return self.create_response(status=200)

    def respond_to_post(self) -> Response:
        controller_response = self.controller.create_use_case_request()
        if isinstance(controller_response, ControllerRejection):
            self.presenter.present_controller_warnings(controller_response)
            return self.create_response(status=400)
        else:
            use_case_response = self.send_work_certificates_to_worker(
                controller_response
            )
            status_code = self.presenter.present_use_case_response(use_case_response)
            return self.create_response(status=status_code)

    def create_response(self, status: int) -> Response:
        workers_list = self.list_workers(
            ListWorkersRequest(company=UUID(current_user.id))
        )
        return Response(
            self.template_renderer.render_template(
                "company/transfer_to_worker.html",
                context=dict(workers_list=workers_list.workers),
            ),
            status=status,
        )
