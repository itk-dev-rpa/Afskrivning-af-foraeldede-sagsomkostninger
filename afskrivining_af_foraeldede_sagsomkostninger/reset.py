"""These functions handle the setup, cleanup, and maintenance of an automation process.
They initiate required applications and resources before execution, ensuring a clean environment.
"""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.sap import sap_login, multi_session, fmcacov

from afskrivining_af_foraeldede_sagsomkostninger import config


def reset(orchestrator_connection: OrchestratorConnection) -> None:
    """Clean up, close/kill all programs and start them again. """
    kill_all()
    open_all(orchestrator_connection)


def kill_all() -> None:
    """Forcefully close all applications used by the robot."""
    sap_login.kill_sap()


def open_all(orchestrator_connection: OrchestratorConnection) -> None:
    """Open all programs used by the robot."""

    # Login to sap
    credentials = orchestrator_connection.get_credential(config.SAP_CREDENTIALS)
    sap_login.login_using_cli(credentials.username, credentials.password)

    # Try to remove the key-popup in SAP before doing anything else
    session = multi_session.get_all_sap_sessions()[0]
    fmcacov.dismiss_key_popup(session)
