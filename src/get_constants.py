from OpenOrchestratorConnection.orchestrator_connection import OrchestratorConnection


class Constants:
    """Define your constants."""
    def __init__(self):
        self.error_email = None


def get_constants(orchestrator_connection: OrchestratorConnection) -> Constants:
    """Get all constants used by the robot."""
    orchestrator_connection.log_trace("Getting constants.")
    constants = Constants()

    # Get email address to send error screenshots to
    constants.error_email = orchestrator_connection.get_constant("Error Email")

    return constants
