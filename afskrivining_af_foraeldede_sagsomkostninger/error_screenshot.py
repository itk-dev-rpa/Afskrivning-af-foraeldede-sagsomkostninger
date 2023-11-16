"""Sends an email with an error report, including a screenshot, when an exception occurs."""
import smtplib
import base64
import traceback
from email.message import EmailMessage
from io import BytesIO
from PIL import ImageGrab
from afskrivining_af_foraeldede_sagsomkostninger import config


def send_error_screenshot(to_address: str | list[str], exception: Exception, process_name: str):
    """Sends an email with an error report, including a screenshot, when an exception occurs.
    Configuration details such as SMTP server, port, sender email, etc., should be set in 'config' module.

    Args:
        to_address (str or list[str]): Email address or list of addresses to send the error report.
        exception (Exception): The exception that triggered the error.
        process_name (str): Name of the process from OpenOrchestrator.
    """

    # Create message
    msg = EmailMessage()
    msg['to'] = to_address
    msg['from'] = config.SCREENSHOT_SENDER
    msg['subject'] = f"Error screenshot: {process_name}"

    # Take screenshot
    screenshot = ImageGrab.grab()
    buffered = BytesIO()
    screenshot.save(buffered, format='PNG')
    screenshot_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Create an HTML message with the embedded image
    html_message = f"""
    <html>
    <body>
    <p>Error type: {type(exception).__name__}</p>
    <p>Error message: {exception}</p>
    <p>{traceback.format_exc()}</p>
    <img src="data:image/png;base64,{screenshot_base64}" alt="Screenshot">
    </body>
    </html>
    """

    msg.set_content("Please enable HTML to view this message.")
    msg.add_alternative(html_message, subtype='html')

    # Send message
    with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.send_message(msg)
