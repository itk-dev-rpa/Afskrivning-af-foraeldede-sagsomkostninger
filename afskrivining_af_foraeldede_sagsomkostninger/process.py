"""The main process where data is prepared and inserted in the queue."""
import json
from itk_dev_shared_components.sap import multi_session
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement
from afskrivining_af_foraeldede_sagsomkostninger.sap_process import recover_to_start_menu, delete_cost
from afskrivining_af_foraeldede_sagsomkostninger import config

def process(orchestrator_connection: OrchestratorConnection, queue_element: QueueElement) -> None:
    """Get a session object to SAP, reset the UI, get queue element and delete cost.
    """
    session = multi_session.get_all_sap_sessions()[0]
    recover_to_start_menu(session)
    data_dict = json.loads(queue_element.data)
    args = orchestrator_connection.process_arguments
    dry_run = True
    if config.DISABLE_DRY_RUN in args:
        dry_run = False

    delete_cost(session=session, fp=data_dict['fp'], aftale=data_dict['aftale'], bilag=data_dict['bilagsnummer'],
                dry_run=dry_run)
