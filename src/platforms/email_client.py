"""Email client for outreach — submissions, library requests, etc."""

import asyncio
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EmailClient:
    """SMTP email client for literary outreach."""

    def __init__(self, host: str, port: int, user: str, password: str, from_name: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.from_name = from_name

    @property
    def is_available(self) -> bool:
        return bool(self.user and self.password)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str = "",
    ) -> bool:
        """Send an email via SMTP SSL."""
        if not self.is_available:
            logger.warning("Email not configured")
            return False

        try:
            import aiosmtplib

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.user}>"
            msg["To"] = to_email

            if body_text:
                msg.attach(MIMEText(body_text, "plain"))
            msg.attach(MIMEText(body_html, "html"))

            await aiosmtplib.send(
                msg,
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                use_tls=True,
            )
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    async def send_query_letter(
        self, to_email: str, agent_name: str, book_title: str, query_body: str
    ) -> bool:
        """Send a query letter to a literary agent or publisher."""
        subject = f"Query: {book_title} by Francisco Angulo de Lafuente"
        html = f"""
        <html><body>
        <p>Dear {agent_name},</p>
        {query_body}
        <p>Best regards,<br>
        Francisco Angulo de Lafuente<br>
        <a href="https://openclaw.ai/">openclaw.ai</a></p>
        </body></html>
        """
        return await self.send_email(to_email, subject, html)

    async def send_library_request(
        self, to_email: str, library_name: str, book_title: str, request_body: str
    ) -> bool:
        """Send a book acquisition request to a library."""
        subject = f"Book Acquisition Suggestion: {book_title}"
        html = f"""
        <html><body>
        <p>Dear {library_name} Acquisitions Team,</p>
        {request_body}
        <p>Thank you for your consideration.</p>
        <p>Best regards,<br>
        OpenCLAW Literary Agent<br>
        On behalf of Francisco Angulo de Lafuente<br>
        <a href="https://openclaw.ai/">openclaw.ai</a></p>
        </body></html>
        """
        return await self.send_email(to_email, subject, html)
