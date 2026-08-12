import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EmailTemplateService:
    def get_welcome_email(self, name: str, link: str) -> str:
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Welcome to SupportGPT AI, {name}!</h2>
            <p>Please click the link below to verify your email address:</p>
            <a href="{link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a>
            <p>If you didn't request this, you can ignore this email.</p>
        </body>
        </html>
        """
        
    def get_ticket_created_email(self, ticket_id: str, title: str) -> str:
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Ticket Created: #{ticket_id}</h2>
            <p>Your ticket "{title}" has been successfully created. Our support team will get back to you shortly.</p>
        </body>
        </html>
        """
        
    def get_ticket_resolved_email(self, ticket_id: str, title: str, summary: str) -> str:
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Ticket Resolved: #{ticket_id}</h2>
            <p>Your ticket "{title}" has been resolved.</p>
            <p><b>Resolution Summary:</b></p>
            <p>{summary}</p>
        </body>
        </html>
        """

    def get_escalation_alert_email(self, agent_id: str, reason: str) -> str:
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: red;">URGENT: Agent Escalation</h2>
            <p>Agent {agent_id} has triggered an escalation alert.</p>
            <p><b>Reason:</b> {reason}</p>
        </body>
        </html>
        """

email_template_service = EmailTemplateService()
