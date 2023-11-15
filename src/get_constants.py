from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection


class Constants:
    """Define your constants."""
    def __init__(self):
        self.error_email = None
        self.dry_run = True
        self.connection_string = None


def get_constants(orchestrator_connection: OrchestratorConnection) -> Constants:
    """Get all constants used by the robot."""
    orchestrator_connection.log_trace("Getting constants.")
    constants = Constants()

    # Get email address to send error screenshots to
    constants.error_email = orchestrator_connection.get_constant("Error Email")

    try:
        orchestrator_connection.get_constant("Activate fosa")
        constants.dry_run = False
    except ValueError:
        orchestrator_connection.log_info("Dry run! SAP data will not be modified.")

    return constants
