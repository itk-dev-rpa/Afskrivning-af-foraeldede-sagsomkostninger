import datetime
from OpenOrchestratorConnection.orchestrator_connection import OrchestratorConnection
from src.get_constants import Constants
from src import config
from src.queue import Database
from src.exceptions import BusinessError
from src.sap_process import SapProcess
from src.queue import Task

def process(orchestrator_connection: OrchestratorConnection, task: Task, constants: Constants) -> None:

    orchestrator_connection.log_trace("Running process.")
    db = Database(table_name=config.TABLE_NAME, connection_string=constants.connection_string)
    sap_process = SapProcess()

    try:
        sap_process.recover_to_start_menu()
        sap_process.delete_cost(fp=task.fp, aftale=task.aftale, bilag=task.bilag, dry_run=constants.dry_run)
        now = datetime.datetime.now()
        db.update_row(row_id=task.row_id, column_data={'status': 'complete',
                      'date_completed':datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)})
    except BusinessError as error:
        orchestrator_connection.log_error(f"{e}: {task.fp, task.aftale, task.bilag}")
        db.update_row(row_id=task.row_id, column_data={'status':f"{type(error).__name__}: {error}"})
