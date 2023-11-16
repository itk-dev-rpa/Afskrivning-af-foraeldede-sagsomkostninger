import json
from afskrivining_af_foraeldede_sagsomkostninger.get_constants import Constants
from afskrivining_af_foraeldede_sagsomkostninger.sap_process import recover_to_start_menu, delete_cost
from itk_dev_shared_components.sap import multi_session
from OpenOrchestrator.database.queues import QueueElement


def process(queue_element: QueueElement , constants: Constants) -> None:
    session = multi_session.get_all_sap_sessions()[0]
    recover_to_start_menu(session)
    data_dict = json.loads(queue_element.data)

    delete_cost(session=session, fp=data_dict['fp'], aftale=data_dict['aftale'], bilag=data_dict['bilagsnummer'],
                dry_run=constants.dry_run)
