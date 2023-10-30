import datetime
from OpenOrchestratorConnection.orchestrator_connection import OrchestratorConnection
from framework.get_constants import Constants
import config
from sql_transactions import Database
from exceptions import BusinessRule, format_message
from sap_process import SapProcess

def process(orchestrator_connection: OrchestratorConnection, constants: Constants) -> None:

    orchestrator_connection.log_trace("Running process.")
    db = Database(table_name=config.TABLE_NAME, connection_string=constants.connection_string)
    sap_process = SapProcess()

    while True:
        row = db.get_new_row()
        if not row:
            print("no jobs left.")
            break
        row_id = row[0]
        aftale = row[1]
        fp = row[2]
        bilag = row[3]

        # NOTICE Retry not included. Implement job queue health?
        try:
            sap_process.recover_to_start_menu()
            sap_process.delete_cost(fp=fp, aftale=aftale, bilag=bilag, dry_run=constants.dry_run)
            now = datetime.datetime.now()
            db.update_row(row_id=row_id, column_data={'status': 'complete',
                          'date_completed':datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)})
        except BusinessRule as e:
            orchestrator_connection.log_info(f"{e}: {fp, aftale, bilag}")
            db.update_row(row_id=row_id, column_data={'status':format_message(e)})
        except Exception as e:
            breakpoint()
            db.update_row(row_id=row_id, column_data={'status':format_message(e)})
            raise e # raise to framework for screenshot and error logging
