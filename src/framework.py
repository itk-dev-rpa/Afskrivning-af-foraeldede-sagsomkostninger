import datetime
import traceback
import sys
from OpenOrchestratorConnection.orchestrator_connection import OrchestratorConnection
from src import get_constants
from src import reset
from src import error_screenshot
from src import process
from src import queue
from src import config
from src.exceptions import BusinessError


def main():
    orchestrator_connection = OrchestratorConnection.create_connection_from_args()
    sys.excepthook = log_exception(orchestrator_connection)

    orchestrator_connection.log_trace("Process started.")

    constants = get_constants.get_constants(orchestrator_connection)
    db = queue.Database(table_name=config.TABLE_NAME, connection_string=constants.connection_string)

    error_count = 0
    max_retry_count = 3
    for _ in range(max_retry_count):
        try:
            orchestrator_connection.log_trace("Resetting.")
            reset.reset(orchestrator_connection)

            orchestrator_connection.log_trace("Running process.")

            while True:
                # job queue loop
                task = db.get_new_task()
                orchestrator_connection.log_trace(f"Getting new task {task.row_id}")
                if not task:
                    break
                try:
                    process.process(orchestrator_connection, task, constants)
                    now = datetime.datetime.now()
                    db.update_row(row_id=task.row_id, column_data={'status': 'complete',
                                                                   'date_completed': datetime.datetime(now.year,
                                                                                                       now.month,
                                                                                                       now.day,
                                                                                                       now.hour,
                                                                                                       now.minute,
                                                                                                       now.second)})

                except BusinessError as error:
                    orchestrator_connection.log_error(f"{error}: {task.fp, task.aftale, task.bilag}")
                    db.update_row(row_id=task.row_id, column_data={'status': f"{type(error).__name__}: {error}"})
            break

        except Exception as error:
            error_count += 1
            db.update_row(row_id=task.row_id, column_data={'status': f"{type(error).__name__}: {error}"})
            error_type = type(error).__name__
            orchestrator_connection.log_error(f"Error caught during process. Number of errors caught: {error_count}. {error_type}: {error}\nTrace: {traceback.format_exc()}")
            error_screenshot.send_error_screenshot(constants.error_email, error, orchestrator_connection.process_name)

    reset.clean_up(orchestrator_connection)
    reset.close_all(orchestrator_connection)
    reset.kill_all(orchestrator_connection)


def log_exception(orchestrator_connection: OrchestratorConnection) -> callable:
    def inner(type, value, traceback):
        orchestrator_connection.log_error(f"Uncaught Exception:\nType: {type}\nValue: {value}\nTrace: {traceback}")
    return inner
