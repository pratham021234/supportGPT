import resend
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY

    async def send_email(self, to_email: str, subject: str, html_body: str):
        # Enqueue to background task simulating Celery
        import asyncio
        asyncio.create_task(self._send_email_task(to_email, subject, html_body))
        return True

    async def _send_email_task(self, to_email: str, subject: str, html_body: str):
        if not settings.RESEND_API_KEY:
            logger.warning(f"Mocking email to {to_email}. Subject: {subject}")
            logger.warning(f"Body: {html_body}")
            return True

        params = {
            "from": "SupportGPT <noreply@supportgpt.ai>",
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }

        try:
            email = resend.Emails.send(params)
            return email
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_verification_email(self, to_email: str, token: str):
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        subject = "Verify your SupportGPT Account"
        html = f"""
        <h2>Welcome to SupportGPT AI!</h2>
        <p>Please click the link below to verify your email address:</p>
        <a href="{verification_link}">{verification_link}</a>
        <p>If you didn't request this, you can ignore this email.</p>
        """
        return await self.send_email(to_email, subject, html)

    async def send_password_reset_email(self, to_email: str, token: str):
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        subject = "Reset your SupportGPT Password"
        html = f"""
        <h2>Password Reset Request</h2>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_link}">{reset_link}</a>
        <p>This link will expire in 24 hours.</p>
        """
        return await self.send_email(to_email, subject, html)

email_service = EmailService()
