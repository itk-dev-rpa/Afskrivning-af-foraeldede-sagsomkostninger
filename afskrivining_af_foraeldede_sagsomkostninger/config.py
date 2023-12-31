"""Framework specific setup"""
SMTP_SERVER = "smtp.aarhuskommune.local"
SMTP_PORT = 25
SCREENSHOT_SENDER = "robot@friend.dk"
# The number of times the robot retries on an error before terminating.
MAX_RETRY_COUNT = 3

# Configuration for the process, where runtime parameters are defined.
QUEUE_NAME = 'Afskrivning-af-foraeldede-sagsomkostninger'
SAP_CREDENTIALS = "Mathias SAP"
ERROR_EMAIL = "Error Email"
DISABLE_DRY_RUN = "disable dry run"
