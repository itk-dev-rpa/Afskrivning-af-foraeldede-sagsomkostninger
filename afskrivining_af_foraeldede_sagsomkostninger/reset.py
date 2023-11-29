"""These functions handle the setup, cleanup, and maintenance of an automation process.
They initiate required applications and resources before execution, ensuring a clean environment.
"""
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.sap import sap_login
from config import SAP_CREDENTIALS

def reset(orchestrator_connection:OrchestratorConnection) -> None:
    """Clean up, close/kill all programs and start them again. """
    kill_all()
    open_all(orchestrator_connection)

def kill_all() -> None:
    """Forcefully close all applications used by the robot."""
    sap_login.kill_sap()

def open_all(orchestrator_connection:OrchestratorConnection) -> None:
    """Open all programs used by the robot."""
    credentials = orchestrator_connection.get_credential(SAP_CREDENTIALS)
    sap_login.login_using_cli(credentials.username, credentials.password)
