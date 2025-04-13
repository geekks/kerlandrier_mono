import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from loguru import logger

def send_email(sender_email: str,
            sender_email_password: str,
            receiver_email: str,
            subject: str,
            message_txt: str,
            message_html: str = None,
            smtp_server: str = "ssl0.ovh.net",
            mail_server_port: int = 465,) -> None:
    """Send email simple SMTP email server."""

    # Create the email
    msg = MIMEMultipart("alternative")
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    if message_html is None:
        message_html = f"<html><body>{message_txt}</body></html>"
    
    # Attach the message to the email
    msg.attach(MIMEText(message_txt, 'plain'))
    msg.attach(MIMEText(message_html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(  host=smtp_server,
                            port=mail_server_port,
                            context=context
                        ) as server:
        server.login(sender_email,
                    sender_email_password
                    )
        server.sendmail(sender_email,
                        receiver_email,
                        msg.as_string()
                        )
    logger.debug(f"Email sent to {receiver_email}")

if __name__ == "__main__":
    send_email("contact@kerlandrier.cc", "Test", "This is a test email.")