import datetime
from OpenOrchestratorConnection.orchestrator_connection import OrchestratorConnection
from framework.get_constants import Constants
import config
from queue import Database
from framework import BusinessError
from sap_process import SapProcess
from queue import Task

def process(orchestrator_connection: OrchestratorConnection, task: Task) -> None:

    orchestrator_connection.log_trace("Running process.")
    db = Database(table_name=config.TABLE_NAME, connection_string=constants.connection_string)
    sap_process = SapProcess()

    # NOTICE Retry not included. Implement job queue health?
    try:
        sap_process.recover_to_start_menu()
        sap_process.delete_cost(fp=task.fp, aftale=task.aftale, bilag=task.bilag, dry_run=constants.dry_run)
        now = datetime.datetime.now()
        db.update_row(row_id=task.row_id, column_data={'status': 'complete',
                      'date_completed':datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)})
    except BusinessError as error:
        orchestrator_connection.log_info(f"{e}: {task.fp, task.aftale, task.bilag}")
        db.update_row(row_id=task.row_id, column_data={'status':f"{type(error).__name__}: {error}"})
