"""This script is designed to run a business process using the OpenOrchestrator framework.
It initializes the orchestrator connection, retrieves constants,
and runs a process in a loop with error handling and retry mechanisms.

This script is designed to be executed as the main entry point for the automation process.
"""
import traceback
import sys
from OpenOrchestrator.database.queues import QueueStatus
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from afskrivining_af_foraeldede_sagsomkostninger import reset
from afskrivining_af_foraeldede_sagsomkostninger import error_screenshot
from afskrivining_af_foraeldede_sagsomkostninger import process
from afskrivining_af_foraeldede_sagsomkostninger.exceptions import BusinessError
from afskrivining_af_foraeldede_sagsomkostninger import config


def main():
    """OpenOrchestrator runs this method when a trigger is activated."""
    orchestrator_connection = OrchestratorConnection.create_connection_from_args()
    sys.excepthook = log_exception(orchestrator_connection)

    orchestrator_connection.log_trace("Process started.")

    error_email = orchestrator_connection.get_constant(config.ERROR_EMAIL)

    error_count = 0

    for _ in range(config.MAX_RETRY_COUNT):
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
                    reset.kill_all()
                    return

                orchestrator_connection.log_trace(f"Getting new task; ID {queue_element.id}.")

                try:
                    process.process(orchestrator_connection, queue_element)
                    orchestrator_connection.set_queue_element_status(element_id=queue_element.id,
                                                                     status=QueueStatus.DONE)

                except BusinessError as error:
                    orchestrator_connection.log_error(f"{error}: {queue_element}")
                    orchestrator_connection.set_queue_element_status(element_id=queue_element.id,
                                                                     status=QueueStatus.FAILED,
                                                                     message=f"{type(error).__name__}: {error}")
            break

        except Exception as error:  # pylint: disable=broad-exception-caught
            error_count += 1
            if queue_element:
                orchestrator_connection.set_queue_element_status(element_id=queue_element.id,
                                                                 status=QueueStatus.FAILED,
                                                                 message=f"{type(error).__name__}: {error}")
            error_type = type(error).__name__
            orchestrator_connection.log_error(f"Error caught during process. Number of errors caught: {error_count}."
                                              f"{error_type}: {error}\nTrace: {traceback.format_exc()}")
            error_screenshot.send_error_screenshot(error_email.value, error, orchestrator_connection.process_name)

    reset.kill_all()


def log_exception(orchestrator_connection: OrchestratorConnection) -> callable:
    """Catch unexpected exceptions."""
    def inner(type, value, traceback):  # pylint: disable=redefined-builtin, redefined-outer-name
        orchestrator_connection.log_error(f"Uncaught Exception:\nType: {type}\nValue: {value}\nTrace: {traceback}")
    return inner


if __name__ == '__main__':
    main()
