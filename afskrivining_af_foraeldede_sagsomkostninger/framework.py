import traceback
import sys
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from afskrivining_af_foraeldede_sagsomkostninger import get_constants
from afskrivining_af_foraeldede_sagsomkostninger import reset
from afskrivining_af_foraeldede_sagsomkostninger import error_screenshot
from afskrivining_af_foraeldede_sagsomkostninger import process
from afskrivining_af_foraeldede_sagsomkostninger.exceptions import BusinessError
import config
from OpenOrchestrator.database.queues import QueueStatus

def main():
    orchestrator_connection = OrchestratorConnection.create_connection_from_args()
    sys.excepthook = log_exception(orchestrator_connection)

    orchestrator_connection.log_trace("Process started.")

    constants = get_constants.get_constants(orchestrator_connection)

    error_count = 0
    max_retry_count = 3
    for _ in range(max_retry_count):
        try:
            orchestrator_connection.log_trace("Resetting.")
            reset.reset(orchestrator_connection)

            orchestrator_connection.log_trace("Running process.")

            while True:
                # job queue loop
                queue_element = orchestrator_connection.get_next_queue_element(queue_name=config.QUEUE_NAME,
                                                                              set_status=True)
                if queue_element is None:
                    orchestrator_connection.log_info("Queue is empty.")
                    clean_up(orchestrator_connection)
                    return

                orchestrator_connection.log_trace(f"Getting new task; ID {queue_element.id}.")

                try:
                    process.process(queue_element, constants)
                    orchestrator_connection.set_queue_element_status(element_id=queue_element.id,
                                                                     status=QueueStatus.DONE)

                except BusinessError as error:
                    orchestrator_connection.log_error(f"{error}: {queue_element}")
                    orchestrator_connection.set_queue_element_status(element_id=queue_element.id,
                                                                     status=QueueStatus.FAILED,
                                                                     message=f"{type(error).__name__}: {error}")
            break

        except Exception as error:
            error_count += 1
            orchestrator_connection.set_queue_element_status(element_id=queue_element.id,
                                                             status=QueueStatus.FAILED,
                                                             message=f"{type(error).__name__}: {error}")
            error_type = type(error).__name__
            orchestrator_connection.log_error(f"Error caught during process. Number of errors caught: {error_count}."
                                              f"{error_type}: {error}\nTrace: {traceback.format_exc()}")
            error_screenshot.send_error_screenshot(constants.error_email, error, orchestrator_connection.process_name)

    clean_up(orchestrator_connection)

def clean_up(orchestrator_connection: OrchestratorConnection): # TODO introduce this to framework
    reset.clean_up(orchestrator_connection)
    reset.close_all(orchestrator_connection)
    reset.kill_all(orchestrator_connection)


def log_exception(orchestrator_connection: OrchestratorConnection) -> callable:
    def inner(type, value, traceback):
        orchestrator_connection.log_error(f"Uncaught Exception:\nType: {type}\nValue: {value}\nTrace: {traceback}")
    return inner

if __name__ == '__main__':
    main()
