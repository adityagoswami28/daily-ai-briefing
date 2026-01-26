"""Gmail SMTP email sender."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from src.utils import get_logger

logger = get_logger(__name__)


class GmailSender:
    """Sends emails using Gmail SMTP."""

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    def __init__(self, gmail_user: str, gmail_app_password: str):
        """
        Initialize Gmail sender.

        Args:
            gmail_user: Gmail email address.
            gmail_app_password: Gmail app password (not regular password).
        """
        self.gmail_user = gmail_user
        self.gmail_app_password = gmail_app_password

    def send(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        from_name: str = "Daily AI Briefing",
    ) -> bool:
        """
        Send email via Gmail SMTP.

        Args:
            to_email: Recipient email address.
            subject: Email subject.
            html_content: HTML email body.
            text_content: Plain text fallback.
            from_name: Display name for sender.

        Returns:
            True if sent successfully, False otherwise.
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{from_name} <{self.gmail_user}>"
            msg["To"] = to_email

            # Attach plain text and HTML versions
            part1 = MIMEText(text_content, "plain", "utf-8")
            part2 = MIMEText(html_content, "html", "utf-8")

            # HTML should be last (preferred)
            msg.attach(part1)
            msg.attach(part2)

            # Send via SMTP
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                server.login(self.gmail_user, self.gmail_app_password)
                server.sendmail(self.gmail_user, to_email, msg.as_string())

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            logger.error("Make sure you're using a Gmail App Password, not your regular password")
            return False

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
