from OpenOrchestratorConnection.orchestrator_connection import OrchestratorConnection
from src.get_constants import Constants
from src.sap_process import recover_to_start_menu, delete_cost
from src.queue import Task
from ITK_dev_shared_components.SAP import multi_session


def process(orchestrator_connection: OrchestratorConnection, task: Task, constants: Constants) -> None:
    session = multi_session.get_all_SAP_sessions()[0]
    recover_to_start_menu(session)
    delete_cost(session=session, fp=task.fp, aftale=task.aftale, bilag=task.bilag, dry_run=constants.dry_run)
